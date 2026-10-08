# Laboratório de GitOps com Argo CD

## Para começar

GitOps registra no Git o estado que queremos no cluster. O Argo CD compara essa intenção com o que está executando. Requer o quickstart completo e acesso do cluster ao GitHub e aos repositórios de charts.

```bash
make gitops
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry -n argocd get applications
```

A Application `demo` deve atingir `Synced` e `Healthy`. `Synced` indica alinhamento com os manifests; `Healthy` indica saúde segundo as regras do Argo CD. Isso não comprova todos os requisitos de negócio de uma aplicação.

## Acesse a interface localmente

```bash
kubectl --context kind-kubefoundry -n argocd port-forward service/argocd-server 8443:443 --address 127.0.0.1
```

Abra `https://127.0.0.1:8443`. O certificado inicial não é emitido para esse endereço por uma autoridade pública. Em outro terminal, com o mesmo `KUBECONFIG`, obtenha a senha inicial somente quando for fazer login

```bash
kubectl --context kind-kubefoundry -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 --decode
```

Use o usuário `admin`. O comando imprime uma credencial. Não a inclua em prints, logs compartilhados ou issues. Para uso compartilhado, configure identidade e RBAC próprios e remova o acesso administrativo inicial.

## Faça uma mudança em seu fork

Crie um fork e ajuste `repoURL` em `gitops/clusters/local/demo.yaml` e a origem permitida em `gitops/projects/playground.yaml`. O exemplo de ApplicationSet também contém a URL original. Execute `make gitops` depois de ajustar os arquivos usados.

Altere uma configuração do chart por PR no seu fork. Após o merge, acompanhe a Application e o rollout. Não é necessário ter permissão de escrita neste repositório para fazer o exercício.

## Para aprofundar

`selfHeal` corrige divergências no cluster. `prune` pode remover recursos que saíram do estado desejado. Revise exclusões com o mesmo cuidado que adições.

O exemplo em `gitops/applicationsets/demo.yaml` gera Applications a partir de uma lista. É uma alternativa ao objeto Application do quickstart. Para trocar, confirme que a Application original não tem finalizer de exclusão em cascata e remova somente esse objeto, preservando os workloads, antes de aplicar o ApplicationSet. Não instale os dois gerenciando a mesma release.

Mais entradas na lista não bastam para operar vários clusters. É necessário cadastrá-los, fornecer credenciais e autorizar seus destinos no AppProject. Esta etapa não é automatizada pela base atual.

Referência — [bootstrap do Argo CD](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/).


[Voltar ao índice](../README.md)
