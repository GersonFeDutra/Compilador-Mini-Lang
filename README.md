# Compilador Mini-Lang

Assignment instructions at [./projeto_final.pdf](./projeto_final.pdf).

## Install

### Linux

Simply run [`./scripts/install.sh`](./scripts/insttall.sh)

### Others

All the dependencies are listed at [`requirements.txt`](./requirements.txt). You can install then with it using `pip`.
See [`./scripts/install.sh`](./scripts/insttall.sh) for an example.

## Run

### Linux

<details>

<summary>You can either run <a src="./minilang">./minilang</a>:</summary>

```bash
chmod +x ./minilang
./minilang
```

</details>
<details>
<summary>Or by activating the <a src="./venv"><code>venv</code></a> environment first, than calling the <a src="./src/compiler.py">compiler</a> module directly:</summary>

```bash
activate_path=bin/activate # e.g. (bash)
source .venv/$activate_path
```

```bash
python -m src.compiler
```

</details>

> [!TIP]
> You can run any layer from the compiler as a module:
> ```bash
> python -m src.modules.lexer
> ```

### VsCode

O arquivo [.vscode/launch.json](.vscode/launch.json) contém algumas instruções de execução e debug para serem usadas com a [IDE VsCode](https://code.visualstudio.com/docs/debugtest/debugging). Após o seu ambiente estar configurado com as extensões recomendadas em [.vscode/extensions.json](.vscode/extensions.json) pressione `F5` e escolha uma das tarefas de execução.

> [!NOTE]
> A flag `--debug-compiler` do compilador Mini-Lang permite que os erros emitidos pelo processo de compilação não sejam capturados, assim repassando-os para o debugger do python.

### Others

1. First you need to create the environment:
    ```bash
    python -m venv ./venv
    ```
2. Than source it:
    ```powershell
    $ActivatePath=Scripts\Activate # eg. windows powershell 2
    .\venv\$ActivatePath
    ```
3. With the venv activated install the requirements:
    ```bash
    pip install -r requirements.txt
    ```
4. Finally run it:
    ```bash
    # from this project root folder
    python -m src.compiler --help
    ```

> [!TIP]
> Use `python compiler.py --help` for more options. See [`./scripts/run.sh`](./scripts/run.sh) for an example.
>
> In fact, you can call it on most of the compiler [submodules](./src/modules/) - those with the `__main__` functions.
