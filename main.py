import os
import asyncio
import subprocess
import shutil
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

DOWNLOAD_FOLDER = './telegram_videos'
COMPRESSED_FOLDER = './telegram_videos_compressed'
GRUPO_URL = os.getenv('GRUPO_URL')

WINRAR_PATH = os.getenv('WINRAR_PATH', r"C:\Program Files\WinRAR\WinRAR.exe")
COMPRESS_INDIVIDUAL = True
COMPRESSION_LEVEL = 5
DELETE_ORIGINALS = True
BATCH_SIZE = 10

class WinRARCompressor:
    def __init__(self, winrar_path, compression_level=5):
        self.winrar_path = winrar_path
        self.compression_level = compression_level
        self.check_winrar()
    
    def check_winrar(self):
        if not os.path.exists(self.winrar_path):
            alternative_paths = [
                r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
                r"C:\Program Files\WinRAR\WinRAR.exe",
                "winrar.exe"
            ]
            
            for path in alternative_paths:
                if os.path.exists(path) or shutil.which(path):
                    self.winrar_path = path
                    print(f"WinRAR encontrado em: {path}")
                    return
            
            raise FileNotFoundError(
                "WinRAR não encontrado! Instale o WinRAR ou ajuste o caminho WINRAR_PATH"
            )
        else:
            print(f"WinRAR encontrado em: {self.winrar_path}")
    
    def compress_file(self, file_path, output_folder):
        if not os.path.exists(file_path):
            return False
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        rar_path = os.path.join(output_folder, f"{base_name}.rar")
        
        command = [
            self.winrar_path,
            "a",
            f"-m{self.compression_level}",
            "-ep1",
            "-y",
            rar_path,
            file_path
        ]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Compactado: {os.path.basename(rar_path)}")
                return True
            else:
                print(f"✗ Erro ao compactar {os.path.basename(file_path)}: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Erro ao executar WinRAR: {e}")
            return False
    
    def compress_batch(self, file_list, output_path):
        if not file_list:
            return False
        
        output_folder = os.path.dirname(output_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        command = [
            self.winrar_path,
            "a",
            f"-m{self.compression_level}",
            "-ep1",
            "-y",
            output_path
        ] + file_list
        
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Lote compactado: {os.path.basename(output_path)}")
                return True
            else:
                print(f"✗ Erro ao compactar lote: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Erro ao executar WinRAR: {e}")
            return False

class TelegramVideoDownloader:
    def __init__(self, api_id, api_hash, phone_number, enable_compression=True):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session', api_id, api_hash)
        
        self.enable_compression = enable_compression
        self.compressor = None
        if enable_compression:
            try:
                self.compressor = WinRARCompressor(WINRAR_PATH, COMPRESSION_LEVEL)
                print("✓ Compactação com WinRAR habilitada")
            except FileNotFoundError as e:
                print(f"⚠️ {e}")
                print("Continuando sem compactação...")
                self.enable_compression = False
        
    async def connect_and_auth(self):
        print("Conectando ao Telegram...")
        await self.client.start()
        
        if not await self.client.is_user_authorized():
            print(f"Enviando código de verificação para {self.phone_number}")
            await self.client.send_code_request(self.phone_number)
            
            try:
                code = input('Digite o código de verificação: ')
                await self.client.sign_in(self.phone_number, code)
            except SessionPasswordNeededError:
                password = input('Digite sua senha de duas etapas: ')
                await self.client.sign_in(password=password)
        
        print("Autenticado com sucesso!")
    
    async def get_group_entity(self, group_link):
        try:
            if '/c/' in group_link:
                group_id = group_link.split('/c/')[1].split('/')[0]
                group_id = int('-100' + group_id)
            else:
                group_username = group_link.split('/')[-1]
                group_id = group_username
            
            entity = await self.client.get_entity(group_id)
            return entity
        except Exception as e:
            print(f"Erro ao obter grupo: {e}")
            return None
    
    async def download_videos(self, group_entity, download_folder):
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        if self.enable_compression and not os.path.exists(COMPRESSED_FOLDER):
            os.makedirs(COMPRESSED_FOLDER)
        
        print(f"Buscando mensagens no grupo...")
        
        video_count = 0
        downloaded_count = 0
        compressed_count = 0
        batch_files = []
        
        async for message in self.client.iter_messages(group_entity):
            if message.media:
                if (isinstance(message.media, MessageMediaDocument) and 
                    message.media.document and 
                    message.media.document.mime_type and
                    message.media.document.mime_type.startswith('video/')):
                    
                    video_count += 1
                    
                    file_extension = message.media.document.mime_type.split('/')[-1]
                    if file_extension not in ['mp4', 'avi', 'mov', 'mkv']:
                        file_extension = 'mp4'
                    
                    filename = f"video_{message.id}_{video_count}.{file_extension}"
                    filepath = os.path.join(download_folder, filename)
                    
                    already_processed = False
                    
                    if self.enable_compression and COMPRESS_INDIVIDUAL:
                        rar_filename = f"video_{message.id}_{video_count}.rar"
                        rar_filepath = os.path.join(COMPRESSED_FOLDER, rar_filename)
                        if os.path.exists(rar_filepath):
                            print(f"Arquivo já compactado: {rar_filename}")
                            downloaded_count += 1
                            already_processed = True
                    else:
                        if os.path.exists(filepath):
                            print(f"Arquivo já existe: {filename}")
                            downloaded_count += 1
                            already_processed = True
                            
                            if (self.enable_compression and not COMPRESS_INDIVIDUAL and 
                                len(batch_files) < BATCH_SIZE):
                                batch_files.append(filepath)
                    
                    if already_processed:
                        continue
                    
                    try:
                        print(f"Baixando vídeo {video_count}: {filename}")
                        await self.client.download_media(message, filepath)
                        downloaded_count += 1
                        print(f"✓ Download concluído: {filename}")
                        
                        if self.enable_compression and self.compressor:
                            if COMPRESS_INDIVIDUAL:
                                if self.compressor.compress_file(filepath, COMPRESSED_FOLDER):
                                    compressed_count += 1
                                    if DELETE_ORIGINALS:
                                        os.remove(filepath)
                                        print(f"  → Original removido para economizar espaço")
                            else:
                                batch_files.append(filepath)
                                
                                if len(batch_files) >= BATCH_SIZE:
                                    batch_name = f"lote_{compressed_count + 1}.rar"
                                    batch_path = os.path.join(COMPRESSED_FOLDER, batch_name)
                                    
                                    if self.compressor.compress_batch(batch_files, batch_path):
                                        compressed_count += 1
                                        if DELETE_ORIGINALS:
                                            for f in batch_files:
                                                if os.path.exists(f):
                                                    os.remove(f)
                                            print(f"  → {len(batch_files)} originais removidos")
                                    
                                    batch_files = []
                        
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"✗ Erro ao baixar {filename}: {e}")
        
        if (self.enable_compression and self.compressor and not COMPRESS_INDIVIDUAL and 
            batch_files):
            batch_name = f"lote_final_{compressed_count + 1}.rar"
            batch_path = os.path.join(COMPRESSED_FOLDER, batch_name)
            
            if self.compressor.compress_batch(batch_files, batch_path):
                compressed_count += 1
                if DELETE_ORIGINALS:
                    for f in batch_files:
                        if os.path.exists(f):
                            os.remove(f)
                    print(f"  → {len(batch_files)} originais finais removidos")
        
        print(f"\n=== RESUMO ===")
        print(f"Total de vídeos encontrados: {video_count}")
        print(f"Vídeos baixados com sucesso: {downloaded_count}")
        
        if self.enable_compression:
            print(f"Arquivos compactados: {compressed_count}")
            if COMPRESS_INDIVIDUAL:
                print(f"Modo: Compactação individual (1 RAR por vídeo)")
            else:
                print(f"Modo: Compactação em lotes ({BATCH_SIZE} vídeos por RAR)")
            print(f"Pasta compactados: {COMPRESSED_FOLDER}")
            
            if DELETE_ORIGINALS:
                print(f"✓ Arquivos originais removidos para economizar espaço")
        
        print(f"Pasta de download: {download_folder}")
        
        if self.enable_compression and compressed_count > 0:
            self.calculate_space_savings(download_folder)
    
    
    def calculate_space_savings(self, download_folder):
        try:
            original_size = 0
            if os.path.exists(download_folder):
                for file in os.listdir(download_folder):
                    file_path = os.path.join(download_folder, file)
                    if os.path.isfile(file_path):
                        original_size += os.path.getsize(file_path)
            
            compressed_size = 0
            if os.path.exists(COMPRESSED_FOLDER):
                for file in os.listdir(COMPRESSED_FOLDER):
                    if file.endswith('.rar'):
                        file_path = os.path.join(COMPRESSED_FOLDER, file)
                        compressed_size += os.path.getsize(file_path)
            
            if compressed_size > 0:
                if original_size > 0:
                    savings_percent = ((original_size - compressed_size) / original_size) * 100
                    print(f"\n💾 ECONOMIA DE ESPAÇO:")
                    print(f"Tamanho original: {self.format_bytes(original_size)}")
                    print(f"Tamanho compactado: {self.format_bytes(compressed_size)}")
                    print(f"Economia: {self.format_bytes(original_size - compressed_size)} ({savings_percent:.1f}%)")
                else:
                    print(f"\n💾 Tamanho total compactado: {self.format_bytes(compressed_size)}")
        except Exception as e:
            print(f"Erro ao calcular economia: {e}")
    
    def format_bytes(self, bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    async def run(self, grupo_url, download_folder):
        try:
            await self.connect_and_auth()
            
            group_entity = await self.get_group_entity(grupo_url)
            if not group_entity:
                print("Não foi possível acessar o grupo. Verifique se você tem acesso.")
                return
            
            print(f"Grupo encontrado: {group_entity.title}")
            
            if self.enable_compression:
                print(f"🗜️  Compactação automática ATIVADA")
                print(f"   Nível de compressão: {COMPRESSION_LEVEL}/5")
                if COMPRESS_INDIVIDUAL:
                    print(f"   Modo: Individual (1 RAR por vídeo)")
                else:
                    print(f"   Modo: Lotes ({BATCH_SIZE} vídeos por RAR)")
                print(f"   Deletar originais: {'Sim' if DELETE_ORIGINALS else 'Não'}")
            else:
                print("📁 Apenas download (sem compactação)")
            
            print(f"Iniciando download dos vídeos...")
            
            await self.download_videos(group_entity, download_folder)
            
        except Exception as e:
            print(f"Erro durante a execução: {e}")
        finally:
            await self.client.disconnect()

async def main():
    print("🗜️  Deseja usar compactação automática com WinRAR?")
    print("   Isso economiza muito espaço mas requer WinRAR instalado.")
    use_compression = input("   (S/n): ").lower().strip()
    use_compression = use_compression != 'n'
    
    downloader = TelegramVideoDownloader(API_ID, API_HASH, PHONE_NUMBER, use_compression)
    
    await downloader.run(GRUPO_URL, DOWNLOAD_FOLDER)

if __name__ == "__main__":
    print("=== TELEGRAM VIDEO DOWNLOADER COM COMPACTAÇÃO ===")
    print("Este script baixará todos os vídeos do grupo especificado.")
    print("🗜️  NOVO: Compactação automática com WinRAR para economizar espaço!")
    print("\n📋 Configurações atuais de compactação:")
    print(f"   • Modo: {'Individual (1 RAR/vídeo)' if COMPRESS_INDIVIDUAL else f'Lotes ({BATCH_SIZE} vídeos/RAR)'}")
    print(f"   • Nível: {COMPRESSION_LEVEL}/5 (máxima compressão)")
    print(f"   • Deletar originais: {'Sim' if DELETE_ORIGINALS else 'Não'}")
    print(f"   • Caminho WinRAR: {WINRAR_PATH}")
    print("\n⚙️  Para alterar essas configurações, edite as variáveis no início do script.")
    print("📋 Certifique-se de ter configurado suas credenciais da API corretamente.\n")
    
    asyncio.run(main())