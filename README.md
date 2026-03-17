# Sistema de Controle de Material

Aplicação web em **Flask** para controle de materiais da **4ª Seção da 6ª Cia Com Mec**, com autenticação de usuários, permissões por classe logística e gestão de inventário por módulos.

## Resumo do site

O sistema centraliza o cadastro, atualização, consulta e auditoria de materiais militares em diferentes classes de suprimento:

- **Classe I (CL1)**: controle de rações, validade, cardápios, lote e histórico de alterações.
- **Classe II (CL2)**: controle de materiais com quantidades previstas/disponíveis/indisponíveis, cálculo de necessidade e geração de PDF.
- **Classe VI (CL6)**: cadastro patrimonial e de disponibilidade de materiais com dados de identificação.
- **Classe VII (CL7)**: controle de materiais por pelotão, com foco operacional.
- **Classe IX (CL9)**: controle de viaturas, situação, localização, destino/missão e histórico de mudanças.

Além do inventário, o site inclui:

- **Login e controle de acesso** por perfil e por classe de material.
- **Dashboard** com atalhos para cada módulo.
- **Administração de usuários** (criação, edição e gestão de permissões).
- **Páginas institucionais** de termos e política de privacidade.
- **Rota de healthcheck** (`/healthz`) para monitoramento.

## Execução

Consulte `requirements.txt` e execute a aplicação com `python app.py` (ou via `wsgi.py`/Gunicorn em produção).
