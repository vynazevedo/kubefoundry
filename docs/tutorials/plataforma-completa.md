# Execute as trilhas de plataforma

A trilha básica ensina os recursos. Estes perfis conectam os recursos em cenários de operação. Você pode executar um por vez e observar o que muda, ou reproduzir a suíte inteira.

## Preparação

Use um cluster descartável do KubeFoundry. Execute `make tools` e `make up` se ainda não o criou. Os perfis usam namespaces dedicados com prefixo `kf-`, além dos namespaces dos controllers. Não se conectam a contas de nuvem nem criam um endpoint público.

Planeje inicialmente 6 CPUs e 12 GiB disponíveis ao Docker para executar todos os componentes juntos. Isso é uma estimativa para planejamento, não capacidade mínima medida. Os testes de CPU geram carga limitada e podem competir com outros programas. A suíte pode levar vários minutos, especialmente esperando métricas e estabilização do autoscaling.

```bash
make advanced-up
make configuration-test storage-test tenancy-test
make observability-up observability-test
make autoscaling-test
make recovery-test
make gateway-test canary-test
make secrets-test operator-test signatures-test
make advanced-security
```

Ou, com cluster e ferramentas prontos

```bash
make advanced-test
```

Execute sequencialmente. Não use `make -j` nesses perfis, pois alguns exercícios atualizam a mesma aplicação. O perfil HPA deve terminar antes de testar contadores da aplicação ou canary. Reexecutar `advanced-up` restaura a configuração básica da aplicação; isso não apaga o PVC.

## O que cada etapa comprova

| Etapa | Evidência exigida |
| --- | --- |
| Configuração | Arquivo montado muda; variável de ambiente só muda após reinício |
| Armazenamento | Conteúdo permanece após substituir o Pod com outro UID |
| Times | Cliente próprio funciona e outro time é bloqueado; RBAC nega acesso cruzado |
| Observabilidade | Falha aparece em métrica, alerta, log e trace consultável pelo ID exato |
| Autoscaling | HPA aumenta réplicas sob carga e volta a uma após a carga |
| Recuperação | Outro banco restaura registros anteriores ao backup e não contém a escrita posterior |
| Gateway | HTTPS funciona validando CA e hostname; sem a CA o certificado é rejeitado |
| Canary | Duas revisões recebem requisições; rollback volta a servir somente a estável |
| Secrets | Duas revisões são sincronizadas sem imprimir valores |
| Operator | Reconciliação, mudança de geração, recriação e coleta de dependentes |
| Assinatura | Artefato original passa e cópia alterada falha |

A suíte é de aprendizagem e validação funcional. Não prova alta disponibilidade, capacidade em escala empresarial ou conformidade de produção. As limitações específicas estão em cada tutorial.

## Limpeza

`make down` remove o cluster e todos os seus dados. Os dumps sintéticos e relatórios locais ficam em `.state/`, ignorada pelo Git. O teste de recuperação remove seus bancos temporários; os outros perfis permanecem instalados para exploração até remover o cluster.


[Voltar ao índice](../README.md)
