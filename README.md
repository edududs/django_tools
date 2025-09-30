# django_tools 🛠️

Coleção em evolução de utilitários que padronizam configurações de projetos Django para APIs. A biblioteca reúne peças reutilizáveis que simplificam bootstrap de projetos internos e servem como base para futuras expansões.

## ✨ Visão geral

- `settings.DjangoSettings`: classe Pydantic que centraliza configurações padrão (segurança, banco de dados, logging e Celery) carregadas via `.env`.
- `settings.consts`: constantes e mapeamentos usados para exportar configurações em formato `dict` compatível com Django.
- `utils.setup`: auxiliares para preparar o ambiente Django em scripts standalone.
- `kiwi.celery`: aplicação Celery pré-configurada para consumir as variáveis `CELERY_` do Django.

## 🚧 Estado do projeto

- Versão inicial (`0.1.0`) ainda em construção.
- API sujeita a alterações sem aviso prévio.
- Documentação tende a crescer conforme novas implementações.

## 📚 Documentação

- Conteúdo detalhado, exemplos e guias avançados serão publicados em um espaço dedicado.
- Feedbacks e sugestões ajudam a priorizar os próximos tópicos.

## 📝 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais informações.

---

⭐ Se este projeto te ajudou, considere dar uma estrela!
