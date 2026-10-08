# Terminal, containers e YAML

## Entenda o terminal

O terminal recebe comandos. A pasta atual determina onde caminhos relativos começam. Um comando pode somente consultar, criar recursos ou apagá-los; leia sua intenção antes de executar.

```bash
pwd
ls
cat versions.env
```

`pwd` mostra a pasta atual, `ls` lista arquivos e `cat` exibe o conteúdo de um arquivo. `cd` muda de pasta. `$PWD` representa o caminho atual. `export KUBECONFIG=...` informa ao cliente Kubernetes onde estão as configurações de acesso daquele terminal.

Nos exemplos, uma linha iniciada por `#` é comentário. Não há necessidade de copiá-la. Não copie o símbolo de prompt de outros tutoriais como se fizesse parte do comando.

## Imagem não é container

A imagem é o artefato usado para criar uma execução. O container é uma execução desse artefato. No kind, existem containers que representam nós; dentro desses nós, o runtime executa os containers dos Pods.

Depois de `make image`, podemos executar a aplicação sem Kubernetes

```bash
docker run --rm --name kubefoundry-primeiro-container --read-only --cap-drop ALL --security-opt no-new-privileges --memory 64m --cpus 0.25 -p 127.0.0.1:18080:8080 kubefoundry/demo:0.1.0
```

Em outro terminal

```bash
curl http://127.0.0.1:18080/
```

A resposta identifica `kubefoundry`. Volte ao terminal do container e pressione Ctrl+C. `--rm` remove esse container ao encerrar. A imagem continua disponível. Se a porta estiver ocupada, altere somente `18080` e use a mesma porta no curl.

**Desafio**. Explique o significado das duas portas. Qual delas a aplicação escuta dentro do container?

<details>
<summary>Conferir o raciocínio</summary>

O host aceita conexões em `127.0.0.1:18080` e encaminha para a porta `8080` do container. Usar loopback evita publicar esse exemplo em todas as interfaces de rede do computador.

</details>

## Leia YAML sem decorar

```yaml
metadata:
  name: primeiro-pod
  labels:
    app: primeiro-pod
```

A indentação agrupa dados. `name` e `labels` pertencem a `metadata`; `app` pertence a `labels`. Use espaços, não tabulações. Um hífen no início de uma entrada representa um item de lista, como os containers de um Pod.

Os manifests Kubernetes normalmente declaram `apiVersion`, `kind`, `metadata` e `spec`. A especificação é a intenção; o campo `status`, preenchido pelos componentes do cluster, registra observações.

```bash
cat labs/fundamentos/pod.yaml
kubectl --context kind-kubefoundry explain pod.spec.containers
```

Não é necessário memorizar todos os campos. Aprenda a consultar o schema e a relacionar o arquivo com os recursos criados.

Próxima etapa. [Pod e Deployment](../tutorials/fundamentos-pods.md).

[Voltar ao índice](../README.md)
