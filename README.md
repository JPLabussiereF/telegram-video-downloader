# Telegram Video Downloader

Ferramenta automatizada para download e compactação de vídeos de grupos do Telegram com suporte à compressão WinRAR.

## ✨ Funcionalidades

- 📥 **Download automático** de todos os vídeos de um grupo do Telegram
- 🗜️ **Compactação automática** com WinRAR para economizar espaço
- 📊 **Relatórios de economia** de espaço em disco
- 🔄 **Modo de retomada** - continua downloads interrompidos
- ⚙️ **Configurações flexíveis** - compactação individual ou em lotes
- 🛡️ **Autenticação segura** via API oficial do Telegram

## 📋 Requisitos

### Python e Dependências
- Python 3.7+
- Bibliotecas: `telethon`, `python-dotenv`

### Software Externo (Opcional)
- **WinRAR** - Para funcionalidade de compactação automática
  - Windows: Baixar em [rarlab.com](https://www.rarlab.com/)
  - Alternativas: 7-Zip, PeaZip (requer modificação do código)

### Credenciais do Telegram
- **API ID** e **API Hash** - Obter em [my.telegram.org](https://my.telegram.org/auth)
- **Número de telefone** associado à sua conta Telegram

## 🚀 Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/telegram-video-downloader.git
   cd telegram-video-downloader
   ```

2. **Instale as dependências**
   ```bash
   pip install telethon python-dotenv
   ```

3. **Configure as variáveis de ambiente**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   # ⚠️ CREDENCIAIS SENSÍVEIS - NUNCA COMMITAR ESTE ARQUIVO!
   API_ID=seu_api_id_aqui
   API_HASH=seu_api_hash_aqui
   PHONE_NUMBER=+5511999999999
   GRUPO_URL=https://t.me/c/1234567890/123456
   
   # Configurações opcionais
   WINRAR_PATH=C:\Program Files\WinRAR\WinRAR.exe
   ```

## 🔧 Configuração

### 1. Obter Credenciais da API do Telegram

1. Acesse [my.telegram.org/auth](https://my.telegram.org/auth)
2. Faça login com seu número de telefone
3. Vá em "API Development Tools"
4. Crie uma nova aplicação
5. Copie o `API ID` e `API Hash`

### 2. Encontrar URL do Grupo

**Para grupos públicos:**
```
https://t.me/nome_do_grupo
```

**Para grupos privados:**
1. Abra o grupo no Telegram Desktop/Web
2. Clique em qualquer mensagem com botão direito
3. Selecione "Copy Message Link"
4. A URL será algo como: `https://t.me/c/1234567890/123456`

### 3. Configurar Compactação (Opcional)

No arquivo `main.py`, ajuste as configurações:

```python
COMPRESS_INDIVIDUAL = True  # True = 1 RAR por vídeo, False = lotes
COMPRESSION_LEVEL = 5       # 0-5 (0=sem compressão, 5=máxima)
DELETE_ORIGINALS = True     # Remove arquivos originais após compactar
BATCH_SIZE = 10            # Vídeos por lote (se COMPRESS_INDIVIDUAL = False)
```

## 🎯 Como Usar

### Execução Básica
```bash
python main.py
```

### Primeira Execução
1. Execute o script
2. Digite o código de verificação enviado pelo Telegram
3. Se tiver autenticação de dois fatores, digite a senha
4. Escolha se deseja usar compactação automática
5. O download iniciará automaticamente

### Execuções Subsequentes
- O script lembrará da sua autenticação
- Downloads serão retomados automaticamente se interrompidos

## 📁 Estrutura de Arquivos

```
telegram-video-downloader/
├── main.py                    # Script principal
├── .env                      # Variáveis de ambiente (criar)
├── .env.example             # Exemplo de configuração
├── session.session          # Sessão do Telegram (gerado automaticamente)
├── telegram_videos/         # Vídeos baixados
└── telegram_videos_compressed/ # Arquivos compactados (se habilitado)
```

## ⚠️ Segurança e Boas Práticas

### 🔒 Campos Sensíveis
**NUNCA commite estes dados no repositório:**
- `API_ID` - ID da aplicação Telegram
- `API_HASH` - Hash de autenticação da API
- `PHONE_NUMBER` - Seu número de telefone
- `GRUPO_URL` - URL do grupo privado
- `session.session` - Arquivo de sessão do Telegram

### 🛡️ Recomendações
- ✅ Use sempre arquivo `.env` para credenciais
- ✅ Adicione `.env` e `*.session` ao `.gitignore`
- ✅ Use números com código do país (+55 para Brasil)
- ✅ Verifique se tem acesso ao grupo antes de executar
- ✅ Teste com grupos pequenos primeiro

### 📝 .gitignore Recomendado
```gitignore
.env
*.session
telegram_videos/
telegram_videos_compressed/
__pycache__/
*.pyc
```

## 🐛 Solução de Problemas

### Erro: "WinRAR não encontrado"
- **Solução**: Instale o WinRAR ou ajuste `WINRAR_PATH` no `.env`
- **Alternativa**: Execute sem compactação

### Erro: "Não foi possível acessar o grupo"
- **Causa**: URL incorreta ou sem acesso ao grupo
- **Solução**: Verifique a URL e se você é membro do grupo

### Erro: "Invalid API ID/Hash"
- **Causa**: Credenciais incorretas
- **Solução**: Verifique API_ID e API_HASH no `.env`

### Downloads interrompidos
- **Solução**: Execute novamente - o script detecta arquivos existentes

## 📊 Exemplo de Uso

```bash
$ python main.py

=== TELEGRAM VIDEO DOWNLOADER COM COMPACTAÇÃO ===
Este script baixará todos os vídeos do grupo especificado.
🗜️  NOVO: Compactação automática com WinRAR para economizar espaço!

📋 Configurações atuais de compactação:
   • Modo: Individual (1 RAR/vídeo)
   • Nível: 5/5 (máxima compressão)
   • Deletar originais: Sim

🗜️  Deseja usar compactação automática com WinRAR?
   Isso economiza muito espaço mas requer WinRAR instalado.
   (S/n): S

✓ Compactação com WinRAR habilitada
Conectando ao Telegram...
Autenticado com sucesso!
Grupo encontrado: Meu Grupo de Vídeos
🗜️  Compactação automática ATIVADA
Iniciando download dos vídeos...

Baixando vídeo 1: video_123_1.mp4
✓ Download concluído: video_123_1.mp4
✓ Compactado: video_123_1.rar
  → Original removido para economizar espaço

=== RESUMO ===
Total de vídeos encontrados: 50
Vídeos baixados com sucesso: 50
Arquivos compactados: 50
Modo: Compactação individual (1 RAR por vídeo)

💾 ECONOMIA DE ESPAÇO:
Tamanho original: 2.3 GB
Tamanho compactado: 1.1 GB
Economia: 1.2 GB (52.2%)
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Aviso Legal

- Use apenas em grupos onde você tem permissão para baixar conteúdo
- Respeite os direitos autorais e termos de uso do Telegram
- O desenvolvedor não se responsabiliza pelo uso inadequado da ferramenta
