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

<summary>You can either run <a src="./scripts.run.sh">./scripts/run.sh</a>:</summary>

```bash
chmod +x ./scripts/run.py
./scripts/run.py
```

</details>
<details>
<summary>Or by activating the <a src="./venv"><code>venv</code></a> environment first than calling <a src="./src/compiler.py">compiler</a> directly:</summary>

```bash
#activate_path=bin/activate # e.g. (bash)
source .venv/$activate_path
chmod +x ./src/compiler.py
./src/compiler.py
```

<details>
<summary>You can also call it as a module:</summary>

```bash
python -m src.compiler
```

</details>
</details>

> [!TIP]
> You can run any layer from the compiler as a module:
> ```bash
> python -m src.modules.lexer
> ```

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
    python compiler.py --help
    ```

> [!TIP]
> Use `python compiler.py --help` for more options. See [`./scripts/run.sh`](./scripts/run.sh) for an example.
>
> In fact, you can call it on most of the compiler [submodules](./src/modules/) - those with the `__main__` functions.
