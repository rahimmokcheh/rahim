import json
import asyncio
import cv2
import numpy as np
import pandas as pd
import os
import threading
import torch
import urllib.parse
import re
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from channels.db import database_sync_to_async

# Import pour YOLO et initialisation du modèle
try:
    from ultralytics import YOLO
    
    # Vérification de la disponibilité d'un GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'You are now using {device}')
    print('---------------------------')
    
    # Définir le chemin du modèle - on utilisera un chemin relatif
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, 'FireShield.pt')
    
    # Vérifier si le modèle existe
    if not os.path.exists(MODEL_PATH):
        print(f"ATTENTION: Le modèle n'a pas été trouvé à {MODEL_PATH}")
        # Essayer avec un autre chemin
        MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), 'FireShield.pt')
        if not os.path.exists(MODEL_PATH):
            print(f"ATTENTION: Le modèle n'a pas été trouvé à {MODEL_PATH} non plus")
            MODEL_PATH = None
    
    # Chargement du modèle YOLO
    if MODEL_PATH:
        model = YOLO(MODEL_PATH).to(device)
        print(f"Modèle YOLO chargé avec succès depuis {MODEL_PATH}")
    else:
        model = None
        print("Impossible de trouver le modèle YOLO")
        
except Exception as e:
    print(f"Erreur lors de l'initialisation de YOLO: {str(e)}")
    model = None

class FireShieldConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extraire le nom de la caméra de l'URL et décoder les caractères spéciaux
        cam_name = self.scope['url_route']['kwargs']['cam_name']
        self.cam_name = urllib.parse.unquote(cam_name)
        
        # Créer un nom de groupe valide en remplaçant les caractères non autorisés par des underscores
        valid_group_name = re.sub(r'[^a-zA-Z0-9\-_\.]', '_', self.cam_name)
        self.room_group_name = f'camera_{valid_group_name}'
        
        print(f"Connexion établie pour la caméra: {self.cam_name}, groupe: {self.room_group_name}")
        
        # Rejoindre le groupe de la caméra
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accepter la connexion WebSocket
        await self.accept()
        
        # Envoyer un message de confirmation de connexion
        await self.send(text_data=json.dumps({
            'message': f'Connecté à la caméra {self.cam_name}'
        }))
        
        # Initialiser un flag pour contrôler la boucle de streaming
        self.streaming = True
        
        # Initialiser la tâche de streaming
        self.stream_task = asyncio.create_task(self.start_streaming())
    
    async def disconnect(self, close_code):
        # Arrêter la boucle de streaming
        self.streaming = False
        
        # Annuler la tâche de streaming si elle existe
        if hasattr(self, 'stream_task'):
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
        
        # Quitter le groupe de la caméra
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        print(f"Déconnexion du client pour la caméra: {self.cam_name}")
    
    async def receive(self, text_data=None, bytes_data=None):
        """
        Reçoit des données depuis le client WebSocket
        """
        if bytes_data:  # Si nous avons reçu une image binaire
            try:
                # Traiter l'image de manière asynchrone
                processed_image, detections, filepath = await self.process_image_async(bytes_data)
                
                if processed_image:
                    # Envoyer l'image traitée et les résultats de détection
                    await self.send(bytes_data=processed_image)
                    
                    # Envoyer également les détails des détections au format JSON
                    detection_count = len(detections) if detections is not None else 0
                    await self.send(text_data=json.dumps({
                        'detections_count': detection_count,
                        'filepath': filepath
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'error': f'Erreur de traitement: {filepath}'
                    }))
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'error': f'Erreur: {str(e)}'
                }))
        elif text_data:
            # Si nous recevons des données texte (commandes, etc.)
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            if message == 'get_latest_image':
                # Récupérer la dernière image depuis la caméra ou la base de données
                latest_image = await self.get_latest_image_async()
                if latest_image:
                    await self.send(bytes_data=latest_image)
                else:
                    await self.send(text_data=json.dumps({
                        'error': 'Aucune image disponible'
                    }))
            elif message == 'start_streaming':
                # Redémarrer le streaming s'il a été arrêté
                if not self.streaming:
                    self.streaming = True
                    self.stream_task = asyncio.create_task(self.start_streaming())
            elif message == 'stop_streaming':
                # Arrêter le streaming
                self.streaming = False
            elif message == 'ping':
                # Répondre au ping pour maintenir la connexion active
                await self.send(text_data=json.dumps({
                    'message': 'pong'
                }))
    
    # Nouvelle méthode pour démarrer le streaming continu
    async def start_streaming(self):
        """
        Démarre une boucle qui capture et envoie des images en continu
        """
        try:
            # Ne pas attendre au début pour améliorer la latence initiale
            print(f"Démarrage du streaming pour la caméra: {self.cam_name}")
            
            # Compteur d'échecs consécutifs
            consecutive_failures = 0
            
            # Boucle de streaming
            while self.streaming:
                try:
                    # Récupérer l'image
                    image_data = await self.fetch_camera_image_async()
                    
                    if image_data:
                        # Réinitialiser le compteur d'échecs
                        consecutive_failures = 0
                        
                        # Traiter l'image avec le modèle IA
                        processed_image, detections, filepath = await self.process_image_async(image_data)
                        
                        if processed_image:
                            # Envoyer l'image traitée
                            await self.send(bytes_data=processed_image)
                            
                            # Pas de pause ici pour minimiser la latence
                            
                            # Envoyer les données de détection immédiatement après
                            detection_count = len(detections) if detections is not None else 0
                            await self.send(text_data=json.dumps({
                                'detections_count': detection_count,
                                'filepath': filepath
                            }))
                    else:
                        # Incrémenter le compteur d'échecs
                        consecutive_failures += 1
                        
                        # Message d'erreur
                        print(f"Impossible de récupérer une image pour {self.cam_name} (échec #{consecutive_failures})")
                        
                        # N'envoyer le message d'erreur que tous les 5 échecs pour éviter de surcharger le client
                        if consecutive_failures % 5 == 1:
                            await self.send(text_data=json.dumps({
                                'error': 'Impossible de récupérer une image de la caméra',
                                'camera': self.cam_name
                            }))
                        
                        # Attendre moins longtemps pour les premiers échecs, plus longtemps pour les échecs répétés
                        wait_time = min(1 + consecutive_failures * 0.5, 5)
                        await asyncio.sleep(wait_time)
                        continue
                    
                except Exception as e:
                    consecutive_failures += 1
                    print(f"Erreur dans la boucle de streaming pour {self.cam_name}: {str(e)}")
                    
                    # N'envoyer l'erreur que rarement pour éviter de surcharger le client
                    if consecutive_failures % 5 == 1:
                        await self.send(text_data=json.dumps({
                            'error': f'Erreur de streaming: {str(e)}'
                        }))
                    
                    # Attendre un peu plus longtemps en cas d'erreur
                    await asyncio.sleep(min(1 + consecutive_failures * 0.5, 5))
                    continue
                
                # Pause minimale entre les captures pour éviter de surcharger le serveur
                # Cette valeur peut être ajustée pour équilibrer la latence et la charge serveur
                await asyncio.sleep(0.1)  # 100ms entre chaque frame pour un streaming fluide
                
        except asyncio.CancelledError:
            print(f"Tâche de streaming annulée pour la caméra: {self.cam_name}")
            raise
        except Exception as e:
            print(f"Erreur fatale dans le streaming pour {self.cam_name}: {str(e)}")
    # Méthode pour récupérer une image de la caméra de manière asynchrone
    async def fetch_camera_image_async(self):
        """
        Récupère une image depuis la caméra de manière asynchrone
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.fetch_camera_image)
    
    def fetch_camera_image(self):
        """
        Récupère une image depuis la caméra (version synchrone)
        """
        from Superviseur.models import Cam  # Import ici pour éviter les importations circulaires
        
        try:
            # Vérifier si cette caméra existe
            try:
                cam = Cam.objects.get(name_cam=self.cam_name)
            except Cam.DoesNotExist:
                print(f"Caméra non trouvée: {self.cam_name}")
                return None
            
            # Construire l'URL de la caméra
            if hasattr(cam, 'is_full_rtsp_url') and cam.is_full_rtsp_url and cam.custom_url:
                camera_url = cam.custom_url
                if camera_url.startswith('rtsp://'):
                    parts = camera_url.replace('rtsp://', '').split('/')
                    if len(parts) > 0:
                        ip_port = parts[0]
                        camera_url = f"http://{ip_port}/image.jpeg"
            else:
                ip = cam.adresse_cam
                port = cam.num_port if cam.num_port else "8080"
                camera_url = f"http://{ip}:{port}/image.jpeg"
            
            # Récupérer l'image depuis l'URL
            import requests
            response = requests.get(camera_url, timeout=3)
            
            if response.status_code == 200:
                # Vérifier si c'est bien une image JPEG
                if response.content[:2] == b'\xff\xd8':  # Signature d'en-tête JPEG
                    return response.content
            
            # Si échec, essayer avec d'autres URL possibles
            alternate_paths = ['/shot.jpg', '/video', '/videostream.cgi']
            for path in alternate_paths:
                try:
                    base_url = f"http://{ip}:{port}"
                    alternate_url = f"{base_url}{path}"
                    response = requests.get(alternate_url, timeout=2)
                    if response.status_code == 200 and response.content[:2] == b'\xff\xd8':
                        return response.content
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération d'image pour {self.cam_name}: {str(e)}")
            return None
    
    # Méthode pour envoyer une image à tous les clients connectés à cette caméra
    async def broadcast_image(self, event):
        image_data = event['image_data']
        await self.send(bytes_data=image_data)
    
    # Méthode pour traiter une image de manière asynchrone
    async def process_image_async(self, image_data):
        # Exécuter le traitement d'image dans un thread séparé
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_image, image_data, self.cam_name)
    
    # Méthode pour récupérer la dernière image de manière asynchrone
    async def get_latest_image_async(self):
        # Exécuter la récupération d'image dans un thread séparé
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_latest_image, self.cam_name)
    
    # Méthode synchrone pour traiter l'image (exécutée dans un thread)
    def process_image(self, image_data, cam_name):
        try:
            # Vérifier si le modèle est disponible
            if model is None:
                return None, None, "Le modèle YOLO n'est pas disponible"
                
            # Décoder l'image depuis les bytes
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return None, None, "Impossible de décoder l'image"
            
            # Prédiction des objets dans l'image
            results = model.predict(frame, conf=0.4, save=True)
            res_plotted = results[0].plot()
            
            # Extraction des résultats de détection
            result_df, result_json = self.get_pandas(results, cam_name)
            
            # Création d'un répertoire pour sauvegarder les images détectées
            current_date = datetime.now().strftime("%d_%m_%Y")
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            save_dir = os.path.join(BASE_DIR, "media", "rahimcam", current_date)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Traitement des détections et sauvegarde
            detections_saved = False
            if not result_df.empty:
                frame_with_boxes = frame.copy()
                
                # Dessin des bounding boxes et sauvegarde des images avec détections
                for index, row in result_df.iterrows():
                    class_name = row['class_name']
                    x_min, y_min, x_max, y_max = int(row['x_min']), int(row['y_min']), int(row['x_max']), int(row['y_max'])
                    cv2.rectangle(frame_with_boxes, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(frame_with_boxes, class_name, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Nommer et sauvegarder l'image pour chaque détection
                    timestamp = datetime.now().strftime("%H_%M_%S")
                    filename = f"{timestamp}_{cam_name}_{class_name}.jpg"
                    filepath = os.path.join(save_dir, filename)
                    
                    # Sauvegarder l'image uniquement si c'est la première détection (pour éviter des duplications)
                    if not detections_saved:
                        cv2.imwrite(filepath, frame_with_boxes)
                        detections_saved = True
                        
                        # Lancer un thread pour sauvegarder les résultats
                        threading.Thread(
                            target=self.save_detection_results_sync,
                            args=(cam_name, filepath, result_json)
                        ).start()
                
                # Si aucune détection spécifique n'a été enregistrée, sauvegarder l'image générale
                if not detections_saved:
                    timestamp = datetime.now().strftime("%H_%M_%S")
                    filename = f"{timestamp}_{cam_name}.jpg"
                    filepath = os.path.join(save_dir, filename)
                    cv2.imwrite(filepath, frame_with_boxes)
            else:
                # Sauvegarder l'image originale si aucune détection n'est présente
                timestamp = datetime.now().strftime("%H_%M_%S")
                filename = f"{timestamp}_{cam_name}_no_detection.jpg"
                filepath = os.path.join(save_dir, filename)
                cv2.imwrite(filepath, frame)
            
            # Encoder l'image avec les détections pour l'affichage
            _, jpeg = cv2.imencode('.jpg', res_plotted)
            
            return jpeg.tobytes(), result_df, filepath
        except Exception as e:
            print(f"Erreur lors du traitement de l'image: {str(e)}")
            return None, None, str(e)
    
    # Méthode synchrone pour récupérer la dernière image
    def get_latest_image(self, cam_name):
        from Superviseur.models import Cam, DetectionResult  # Import ici pour éviter les importations circulaires
        
        try:
            # Vérifier si cette caméra existe
            try:
                cam = Cam.objects.get(name_cam=cam_name)
                print(f"Caméra trouvée: {cam.name_cam}")
            except Cam.DoesNotExist:
                print(f"Caméra non trouvée: {cam_name}")
                return None
            
            # Tenter de récupérer directement depuis la caméra
            try:
                # Construire l'URL de la caméra à partir du modèle
                if hasattr(cam, 'is_full_rtsp_url') and cam.is_full_rtsp_url and cam.custom_url:
                    camera_url = cam.custom_url
                    if camera_url.startswith('rtsp://'):
                        parts = camera_url.replace('rtsp://', '').split('/')
                        if len(parts) > 0:
                            ip_port = parts[0]
                            camera_url = f"http://{ip_port}/image.jpeg"
                else:
                    ip = cam.adresse_cam
                    port = cam.num_port if cam.num_port else "8080"
                    camera_url = f"http://{ip}:{port}/image.jpeg"
                
                print(f"Tentative de récupération depuis l'URL: {camera_url}")
                
                # Récupérer l'image depuis l'URL
                import requests
                response = requests.get(camera_url, timeout=3)
                
                if response.status_code == 200:
                    # Vérifier si c'est bien une image JPEG
                    if response.content[:2] == b'\xff\xd8':  # Signature d'en-tête JPEG
                        # Traiter l'image avec le modèle IA
                        processed_image, detections, filepath = self.process_image(response.content, cam_name)
                        
                        if processed_image:
                            return processed_image
                
                # Essayer avec des chemins alternatifs courants pour les caméras IP
                alternate_paths = ['/shot.jpg', '/video', '/videostream.cgi']
                for path in alternate_paths:
                    try:
                        base_url = f"http://{ip}:{port}"
                        alternate_url = f"{base_url}{path}"
                        response = requests.get(alternate_url, timeout=2)
                        if response.status_code == 200 and response.content[:2] == b'\xff\xd8':
                            processed_image, detections, filepath = self.process_image(response.content, cam_name)
                            if processed_image:
                                return processed_image
                    except:
                        continue
                
            except Exception as e:
                print(f"Erreur lors de la récupération depuis la caméra: {str(e)}")
            
            # Si la récupération directe échoue, récupérer la dernière image enregistrée
            try:
                latest_detection = DetectionResult.objects.filter(
                    camera_name__name_cam=cam_name
                ).order_by('-detected_at').first()
                
                if latest_detection and hasattr(latest_detection, 'path_to_image'):
                    filepath = latest_detection.path_to_image
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            return f.read()
            except Exception as e:
                print(f"Erreur lors de la récupération de la détection: {str(e)}")
            
            # Si aucune image n'est disponible, utiliser l'image par défaut
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            default_image_path = os.path.join(BASE_DIR, "static", "profile_pics", "téléchargement.png")
            
            if not os.path.exists(default_image_path):
                # Essayer un autre chemin
                default_image_path = os.path.join(BASE_DIR, "Site_web", "static", "profile_pics", "téléchargement.png")
            
            if os.path.exists(default_image_path):
                with open(default_image_path, 'rb') as f:
                    return f.read()
            
            return None
        except Exception as e:
            import traceback
            print(f"Erreur dans get_latest_image: {str(e)}")
            print(traceback.format_exc())
            return None
    
    # Fonction pour extraire les détections d'objets dans un DataFrame Pandas et un format JSON
    def get_pandas(self, results, cam_name):
        boxes_list = results[0].boxes.data.tolist()
        columns = ['x_min', 'y_min', 'x_max', 'y_max', 'confidence', 'class_id']

        for i in boxes_list:
            i[:4] = [round(coord, 1) for coord in i[:4]]
            i[5] = int(i[5])
            i.append(results[0].names[i[5]])

        columns.append('class_name')
        result_df = pd.DataFrame(boxes_list, columns=columns) if boxes_list else pd.DataFrame(columns=columns)
        result_df['camera_name'] = cam_name

        total_objects = sum(len(result.boxes) for result in results)

        # Gérer le cas où result_df est vide
        if result_df.empty:
            return result_df, {}

        # Créer un fichier temporaire pour les résultats JSON
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            result_df.to_json(temp_file.name, orient='split', compression='infer')
            result_df_json = pd.read_json(temp_file.name, orient='split', compression='infer')

        json_data_str = result_df.to_json(orient='split', compression='infer')

        if json_data_str is not None and total_objects != 0:
            json_data = json.loads(json_data_str)
            print('----------------------------------------------------------------------------------')
            print(f"Ce sont les détections pour la caméra '{cam_name}':")
            print(f'Nombres d\'objets détectés: {total_objects}')
            print(result_df_json)
            return result_df, json_data
        return result_df, json.loads(json_data_str if json_data_str else '{}')
    
    # Fonction pour sauvegarder les résultats en DB (version synchrone pour être utilisée dans un thread)
    def save_detection_results_sync(self, cam_name, filepath, detection_data):
        from Superviseur.models import Cam, DetectionResult  # Import ici pour éviter les importations circulaires
        
        try:
            # Récupérer l'instance de la caméra et ses informations associées
            camera_instance = Cam.objects.get(name_cam=cam_name)
            project_instance = camera_instance.name_project
            client_instance = project_instance.pseudo

            # Créer une nouvelle instance de DetectionResult
            detection_result_instance = DetectionResult(
                camera_name=camera_instance,
                path_to_image=filepath,
                detection_data=detection_data,
                user=client_instance,
            )
            detection_result_instance.save()
            print(f"Résultat de détection sauvegardé pour {cam_name}: {filepath}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des résultats : {e}")
    
    # Version asynchrone pour sauvegarder les résultats en DB
    @database_sync_to_async
    def save_detection_results(self, cam_name, filepath, detection_data):
        self.save_detection_results_sync(cam_name, filepath, detection_data)