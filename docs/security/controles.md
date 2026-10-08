# Segurança que podemos verificar

## Para começar

Uma proteção é mais convincente quando mostramos uma operação legítima funcionando e uma operação proibida sendo bloqueada. Execute depois de implantar a aplicação

```bash
make verify
make security
```

Os testes estão em [tests/security.py](../../tests/security.py). Leia as alterações aplicadas a cada Pod de teste para entender qual regra está sendo exercitada.

| Camada | Comportamento verificado | Limite da evidência |
| --- | --- | --- |
| Pod Security | Pod privilegiado é rejeitado | Não detecta falhas de negócio |
| Admissão nativa | Raiz gravável e token automático são rejeitados | Escopo dos namespaces rotulados |
| Init containers | Raiz gravável é rejeitada | Não equivale a uma auditoria de todos os campos da API |
| Rede | Cliente autorizado passa; não autorizado sofre timeout | Caso específico de entrada na aplicação |
| RBAC | Leitura de logs permitida; secrets e escrita negados | Identidade de observação usada no teste |
| Imagem | govulncheck e Trivy analisam o artefato | Depende da cobertura e das bases consultadas |

## Entenda o teste de rede

Os dois clientes usam o mesmo IP de Service. Assim, uma falha de DNS não é confundida com isolamento. Se um Pod não termina, não consegue baixar a imagem ou não é agendado, o teste falha. Um cliente legítimo precisa funcionar para dar sentido ao bloqueio do outro.

A label de autorização não é uma identidade criptográfica. Um usuário com permissão para criar Pods e escolher labels pode reproduzi-la. O perfil de observação não recebe esse poder; um modelo multi-time precisa considerar essa fronteira explicitamente.

## Para aprofundar

O namespace `playground` recebe Pod Security `restricted`, quotas e limites. As ValidatingAdmissionPolicies usam falha fechada e selecionam namespaces com `kubefoundry.io/workload=true`. Infraestrutura fora desse escopo exige revisão própria.

O teste de RBAC usa impersonação a partir da identidade administrativa do laboratório. Ele verifica autorização do service account observado, não um fluxo completo de autenticação de usuário via OIDC.

O SBOM fica em `.state/demo.cdx.json` e descreve componentes detectados. Gerar SBOM não assina uma imagem, não bloqueia sua execução e não garante ausência de vulnerabilidades desconhecidas. O scanner bloqueia os níveis configurados; resultados precisam ser interpretados, não ignorados automaticamente.

Não versionamos kubeconfigs, chaves ou tokens. Kubernetes Secrets usam codificação base64 para representação e não são, por isso, criptografados. Proteção em repouso e um provedor externo não estão configurados neste laboratório.

Referências. [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) e [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/).


[Voltar ao índice](../README.md)
