# Operação e evolução

## Antes de uma mudança

Leia [versions.env](../../versions.env), confira o contexto e registre qual comportamento deseja alterar. Na base atual, algumas versões também aparecem em `go.mod`, no Makefile e nos rótulos de Pod Security. Atualizá-las exige manter essas referências coerentes.

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry get nodes
kubectl --context kind-kubefoundry -n playground get pods
```

## Como atualizar com evidência

1. Consulte releases e matrizes oficiais dos componentes envolvidos.
2. Ajuste os pins em uma branch e revise breaking changes.
3. Crie um ambiente descartável com a nova combinação.
4. Execute `make check`, o deploy, `make security` e `make verify`.
5. Valide GitOps e o perfil de banco quando a mudança os afetar.
6. Registre os resultados na PR, incluindo limitações.

O CI usa actions fixadas por commit e recebe propostas do Dependabot. As versões dos charts e do arquivo `versions.env` também precisam de acompanhamento; o Dependabot configurado não atualiza todas essas referências.

## Recriar não é atualizar em produção

Para este laboratório descartável, apagar e recriar o kind é um caminho simples para experimentar outra versão. Isso destrói o banco. Não é um procedimento de upgrade de produção nem um exercício de restauração.

Para um serviço real, seria preciso definir RPO, quanto dado podemos perder, e RTO, quanto tempo podemos levar para recuperar. Um backup só passa a ser evidência de recuperação quando é restaurado e seus dados são validados.

## Recuperação de uma mudança de aplicação

Com GitOps, reverta no Git a mudança problemática, revise o resultado renderizado e acompanhe a reconciliação. Alterações de schema ou dados podem não ser reversíveis apenas trocando a imagem. O laboratório demo não implementa migrações de banco.

## Próximas capacidades

Os [perfis avançados](../tutorials/plataforma-completa.md) exercitam isolamento, Gateway API e TLS, telemetria, assinaturas de artefatos, rotação de secrets, entrega gradual e restauração lógica. SLOs de produção, admissão de imagens assinadas e recuperação multi-região exigem decisões que não estão automatizadas neste laboratório.


[Voltar ao índice](../README.md)
