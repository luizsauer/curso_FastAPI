#!/bin/sh

# Executa as migrações do banco de dados
poetry run alembic upgrade head

# Inicia o servidor FastAPI
poetry run uvicorn fast_zero.app:app --host 0.0.0.0 --port 8000 --reload --workers 1 --log-level info

# # Mantém o container ativo
# tail -f /dev/null

# O comando acima mantém o container em execução, permitindo que você acesse o FastAPI na porta 8000.
# Você pode acessar a documentação da API em http://localhost:8000
# E o Swagger UI em http://localhost:8000/docs
# Certifique-se de que o Docker esteja em execução e que o container esteja configurado corretamente
# para que o FastAPI possa ser acessado na porta 8000.
# Se você precisar parar o container, use o comando `docker-compose down` no terminal.
# Isso irá parar e remover o container, mas os dados do banco de dados persistirão no volume definido no compose.yaml.
# Para reiniciar o container, use `docker-compose up -d` para iniciar em segundo plano.
# Se precisar ver os logs do container, use `docker-compose logs -f` para acompanhar os logs em tempo real.
# Para acessar o terminal do container, use `docker exec -it <container_id> /bin/sh`.
# Substitua `<container_id>` pelo ID do seu container FastAPI, que pode ser encontrado com `docker ps`.
# Se você quiser executar comandos específicos dentro do container, como rodar testes ou executar scripts de manutenção,
# você pode fazer isso diretamente no terminal do container após acessá-lo com o comando acima.