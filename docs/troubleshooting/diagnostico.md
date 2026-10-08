# Diagnóstico por sintoma

Comece pelo que você observou. Evite apagar o cluster antes de coletar os eventos; isso pode eliminar a informação que explica o erro.

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry get nodes
kubectl --context kind-kubefoundry get pods -A
kubectl --context kind-kubefoundry -n playground get events --sort-by=.lastTimestamp
```

| Sintoma | Verifique primeiro | Próximo passo |
| --- | --- | --- |
| Docker indisponível | `docker info` | Inicie o Docker e habilite integração WSL se aplicável |
| API com conexão recusada | Cluster ativo e kubeconfig correto | Confirme o Docker e `.bin/kind get clusters` |
| Cluster já existe | Nome e uso do cluster | Reutilize as etapas posteriores; só apague se for descartável |
| Pod Pending | Eventos, recursos e PVCs | Corrija a causa indicada pelo scheduler |
| ImagePullBackOff | Imagem local carregada | Execute `make image`; confira nome e tag no chart |
| CrashLoopBackOff | Logs e última terminação | Use logs atuais e `--previous` quando houver reinício |
| Aplicação sem endpoints | Readiness e labels do Service | Compare seletores e Pods prontos |
| Pod rejeitado | Mensagem completa da API | Ajuste o manifest à regra, sem desabilitar a proteção |
| Argo CD OutOfSync | Diff e repositório configurado | Revise a intenção no Git antes de sincronizar |
| Banco não fica Ready | Eventos, PVC e logs do operator | Verifique armazenamento e capacidade |

## Investigue um Deployment

```bash
kubectl --context kind-kubefoundry -n playground describe deployment demo
kubectl --context kind-kubefoundry -n playground get pods -l app.kubernetes.io/instance=demo
kubectl --context kind-kubefoundry -n playground logs deployment/demo --tail=100
```

`logs deployment/demo` não agrega necessariamente todas as réplicas. Escolha o Pod específico quando investigar diferenças entre elas. A imagem `scratch` não contém shell; `kubectl exec ... -- sh` não é um método de diagnóstico disponível nela.

## O teste de rede falhou

Leia se falhou o cliente permitido ou o proibido. Se o permitido não alcança o serviço, primeiro investigue readiness, endpoints e Cilium. Se o proibido alcança, confira labels, seletores e políticas aplicadas. O teste usa IP direto para não depender de DNS.

## Peça ajuda com contexto

Inclua a etapa, as versões, a mensagem de erro e se o ambiente é Linux, macOS ou WSL. Remova tokens, senha inicial do Argo CD e conteúdo de Secrets. Um print ajuda a localizar o problema, mas a mensagem em texto facilita pesquisa e acessibilidade.


[Voltar ao índice](../README.md)
