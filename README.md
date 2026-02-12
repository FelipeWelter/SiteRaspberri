# SiteRaspberri
Backup, site para rodar no raspberri

## Recuperação de senha por e-mail (Gmail)

Defina as variáveis de ambiente antes de iniciar a aplicação:

- `MAIL_USERNAME`: conta Gmail remetente.
- `MAIL_PASSWORD`: senha de app do Google (não use a senha normal da conta).
- `MAIL_DEFAULT_SENDER` (opcional): remetente exibido.
- `PASSWORD_RESET_MAX_AGE` (opcional): validade do link em segundos (padrão: 3600).

Exemplo:

```bash
export MAIL_USERNAME="seuemail@gmail.com"
export MAIL_PASSWORD="senha_de_app_google"
export MAIL_DEFAULT_SENDER="seuemail@gmail.com"
```
