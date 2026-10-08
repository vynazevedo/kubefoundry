# Isolamento entre times

## Objetivo

Provar operações permitidas e bloqueadas na API e na rede. Requer a imagem de `make advanced-up`.

```bash
make tenancy-test
```

São criados `kf-team-a` e `kf-team-b`, cada um com aplicação, Service, NetworkPolicy, quota, service account de observação e RBAC local.

O cliente de cada time alcança seu próprio Service. O acesso ao Service do outro time precisa falhar por timeout. A identidade de observação pode ler seus Pods, mas não os Secrets nem os Pods do outro time.

## Inspecione sem expor dados

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry -n kf-team-a get resourcequota,networkpolicy,role,rolebinding
kubectl --context kind-kubefoundry -n kf-team-b get resourcequota,networkpolicy,role,rolebinding
```

**Desafio**. Uma Role limita pacotes de rede? Uma NetworkPolicy impede alguém de ler um Secret pela API? Relacione cada proteção à operação que ela controla.

## Para aprofundar

O teste usa impersonação a partir da identidade administrativa do laboratório. Ele não testa login de pessoas, OIDC ou integração com diretórios corporativos. A autoridade que cria namespaces e políticas continua sendo confiável.

O isolamento de rede é de namespace, não de identidade humana. Os testes cobrem os fluxos declarados, não todas as combinações possíveis de DNS, egress, serviços externos e permissões. Um programa multi-tenant de produção precisa revisar essas outras fronteiras e os privilégios dos controllers.


[Voltar ao índice](../README.md)
