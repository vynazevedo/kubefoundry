# Rotação de secrets e verificação de artefatos

## Sincronização de secrets

```bash
make secrets-test
```

O External Secrets usa o provider Kubernetes para ler credenciais fictícias em `kf-secret-source` e materializar um Secret em `kf-platform`. O service account do provider tem acesso somente ao namespace de origem.

O teste altera a origem duas vezes e espera o destino refletir cada revisão, sem imprimir os valores. Também verifica que a identidade não pode ler Secrets de `kube-system`.

Esse é um backend Kubernetes real e restrito, mas ainda dentro do mesmo cluster. O exercício não representa um cofre externo, integração com AWS Secrets Manager ou criptografia em repouso. Sincronizar o Secret também não garante que qualquer aplicação recarregue credenciais automaticamente; isso depende de como ela as consome.

## Assinaturas com controle negativo

Requer o binário produzido por `make advanced-up`.

```bash
make signatures-test
```

O script instala Cosign com checksum verificado, gera uma chave temporária, assina o binário e verifica o original. Depois altera uma cópia e exige que a verificação falhe. Chaves e cópias temporárias são removidas ao encerrar.

O exercício é offline, com chave local. Não utiliza identidade OIDC, transparência pública ou timestamp confiável. O flag que ignora a verificação do transparency log é uma exceção explícita desse cenário, não uma recomendação para pipelines públicos.

## O que a assinatura não faz

Assinar um binário não comprova a identidade de um mantenedor sem uma política de confiança. Este perfil também não instala uma política de admissão que bloqueie imagens não assinadas no cluster. A imagem local ainda é carregada no kind por tag. Para produção, seriam necessários registro, identidade verificável, digest, política de admissão e testes de negação correspondentes.

## Auditoria das aplicações

```bash
make operator-test
make advanced-security
```

A análise usa govulncheck e Trivy nas aplicações workbench e operator e gera SBOMs CycloneDX em `.state/`. As bases mudam ao longo do tempo; um resultado limpo hoje não garante ausência de vulnerabilidades futuras.


[Voltar ao índice](../README.md)
