FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app

# Copia apenas arquivos de dependência primeiro para aproveitar o cache
COPY pyproject.toml poetry.lock* README.md ./

# Instala o poetry
RUN pip install poetry

# Ajuste de performance opcional
RUN poetry config installer.max-workers 10

# Instala as dependências sem as de desenvolvimento
RUN poetry install --no-interaction --no-ansi --without dev --no-root

# Agora copia o restante da aplicação
COPY . .

# Copia o script de entrada e torna executável
# Esse script pode ser usado para configurar o ambiente ou iniciar serviços adicionais
# Exemplo: configurar variáveis de ambiente, iniciar serviços como Redis, etc.
# Certifique-se de que o script entrypoint.sh está no diretório raiz do projeto
# e que ele tem permissões de execução (chmod +x entrypoint.sh)
# Se não tiver esse script, você pode remover essa parte do Dockerfile
# Se não precisar de um entrypoint, pode remover as linhas abaixo
# sed -i 's/\r$//' remove os caracteres de \r do Windows (CRLF), forçando compatibilidade.
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

# Inicia a aplicação
ENTRYPOINT ["/app/entrypoint.sh"]