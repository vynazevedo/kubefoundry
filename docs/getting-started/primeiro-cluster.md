# Seu primeiro cluster

## Objetivo e requisitos

Ao terminar, você terá uma aplicação com duas réplicas e terá executado testes reais de segurança. Reserve inicialmente cerca de 4 CPUs e 8 GiB para o Docker; é uma estimativa de planejamento, não um mínimo medido. Argo CD e PostgreSQL exigem recursos adicionais.

Instale Git, Docker, kubectl, Go, Python 3, curl, tar e make. No Windows, use WSL2 com integração do Docker Desktop habilitada. O projeto baixa o toolchain Go declarado e instala Helm, kind e Trivy em `.bin/`.

Verifique antes de começar

```bash
docker info
kubectl version --client
go version
python3 --version
```

`docker info` precisa mostrar um servidor disponível. Se mostrar somente o cliente ou erro de conexão, resolva isso antes de criar o cluster.

## Execute em etapas

```bash
git clone https://github.com/vynazevedo/kubefoundry.git
cd kubefoundry
make tools
make check
make up
make image deploy
make security
make verify
```

| Comando | O que faz | Como reconhecer sucesso |
| --- | --- | --- |
| `make tools` | Baixa ferramentas e confere checksums | Termina sem erro |
| `make check` | Testa Go e valida chart e scripts | Testes e lint passam |
| `make up` | Cria cluster e instala rede e políticas | Nós ficam Ready |
| `make image deploy` | Compila, carrega imagem e aplica chart | Rollout termina |
| `make security` | Analisa imagem e gera SBOM | Sem achados que bloqueiem o comando |
| `make verify` | Executa casos permitidos e proibidos | Todas as linhas PASS |

Não prossiga ignorando uma falha. A etapa seguinte pode depender de recursos que ainda não existem.

## Conheça o ambiente

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry get nodes
kubectl --context kind-kubefoundry -n playground get deployments,pods,services
kubectl --context kind-kubefoundry -n playground port-forward service/demo 8080:8080 --address 127.0.0.1
```

Mantenha esse terminal aberto e acesse `http://127.0.0.1:8080`. A resposta JSON identifica o serviço `kubefoundry`. Encerre o encaminhamento com Ctrl+C. Ele é um acesso administrativo; o teste de NetworkPolicy é feito entre Pods, por `make verify`.

## Limpeza

```bash
make down
```

Esse comando remove o cluster `kubefoundry` e seus dados, inclusive PostgreSQL se você instalou o perfil de banco. Não remove o código. `make up` recusa adotar um cluster existente com esse nome; não use a limpeza para contornar isso sem confirmar que é um ambiente descartável.


[Voltar ao índice](../README.md)
