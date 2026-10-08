# Prepare seu computador

## O que você precisa

Docker executa os containers que representam os nós do cluster. `kubectl` conversa com a API Kubernetes. Go compila nossa aplicação. Git baixa o projeto. Python e make executam validações e organizam comandos.

Você precisará de acesso à internet para baixar ferramentas, imagens e bases de vulnerabilidades. Comece com a estimativa de 4 CPUs e 8 GiB disponíveis ao Docker. Ela não é um mínimo medido; outros programas competem pelos mesmos recursos.

## Escolha seu sistema

| Sistema | Preparação |
| --- | --- |
| Windows | Instale WSL2 e Docker Desktop com backend WSL2. Habilite a integração da distribuição. Execute os comandos do projeto no terminal Linux do WSL, não no PowerShell |
| macOS | Instale Docker Desktop, inicie-o e use seu terminal. Instale também as ferramentas de linha de comando necessárias ao make |
| Linux | Instale Docker Engine ou Desktop conforme sua distribuição. Confirme acesso ao daemon pelo usuário que executará o laboratório |

Siga os instaladores oficiais, adequados à sua arquitetura. Evite executar scripts desconhecidos com privilégios administrativos.

- [Docker no Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Docker no macOS](https://docs.docker.com/desktop/setup/install/mac-install/)
- [Docker Engine no Linux](https://docs.docker.com/engine/install/)
- [kubectl por sistema operacional](https://kubernetes.io/docs/tasks/tools/)
- [Go](https://go.dev/doc/install), [Git](https://git-scm.com/downloads) e [Python](https://www.python.org/downloads/)

## Confira cada dependência

```bash
git --version
docker info
kubectl version --client
go version
python3 --version
make --version
curl --version
tar --version
```

No `docker info`, procure informações do **Server**. Ter apenas o cliente instalado não basta. Se algum comando não existir, instale a ferramenta antes de seguir. Acesso ao Docker concede poderes elevados sobre a máquina; não resolva um erro de permissão abrindo o socket para todos os usuários.

## Baixe e prepare

```bash
git clone https://github.com/vynazevedo/kubefoundry.git
cd kubefoundry
make tools
make check
make up
make image
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry get nodes
```

Os nós devem ficar `Ready`. `make tools` instala versões fixadas de Helm, kind e Trivy em `.bin/`. O Go baixa o toolchain fixado quando necessário. O cliente kubectl deve ser compatível com o servidor; para esta base, prefira o mesmo minor indicado em `versions.env`.

Abra [terminal, containers e YAML](terminal-containers-yaml.md) antes de aplicar o primeiro Pod. Em novos terminais, entre na raiz do projeto e exporte `KUBECONFIG` novamente.

Se você já executou `make up`, não precisa repeti-lo. O comando recusa adotar um cluster existente. Não apague um ambiente só para repetir uma etapa sem revisar seus dados.

[Voltar ao índice](../README.md)
