# AgroControl CBA

Sistema monolítico de consola desarrollado en Python para gestionar productos, lotes productivos, inventario, ventas, alertas y reportes.

## Requisitos
- Python 3.10 o superior.
- Git para el control de versiones.

No utiliza bases de datos, frameworks web ni librerías externas.

## Ejecución

Desde la carpeta del proyecto:

```bash
python main.py
```

Al iniciar, si los archivos JSON no existen, se crean automáticamente como colecciones vacías.

## Estructura

```text
agrocontrol_cba/
├── main.py
├── data/
│   ├── productos.json
│   ├── lotes.json
│   ├── movimientos.json
│   └── ventas.json
├── README.md
└── .gitignore
```

## Reglas principales
- Los códigos de productos y lotes se almacenan en mayúscula y son únicos.
- Los productos desactivados conservan su historial.
- El stock se calcula a partir de los movimientos.
- No se permiten salidas ni ventas superiores al stock disponible.
- La cosecha genera automáticamente una entrada de inventario.
- Un lote solo puede cosecharse una vez.
- Una venta contiene uno o varios productos y conserva el precio vigente de cada producto.
- Las modificaciones se guardan inmediatamente en JSON.
- Los movimientos y ventas usan identificadores secuenciales.

## Almacenamiento de datos

El sistema utiliza archivos JSON para almacenar la información de productos, lotes, movimientos de inventario y ventas.

Los archivos utilizados son:

- productos.json
- lotes.json
- movimientos.json
- ventas.json

## Gestión de productos

El sistema permite registrar productos con código, nombre, categoría, unidad, precio, stock mínimo y estado.

Los códigos de los productos deben ser únicos y se almacenan en mayúsculas.


## Git y GitHub

Se recomienda realizar commits pequeños y significativos:

```bash
git init
git add .
git commit -m "chore: crea estructura inicial de AgroControl CBA"
git add .
git commit -m "feat: implementa carga y guardado de archivos JSON"
git add .
git commit -m "feat: agrega gestion y validacion de productos"
git add .
git commit -m "feat: implementa registro y cosecha de lotes"
git add .
git commit -m "feat: agrega movimientos y calculo de stock"
git add .
git commit -m "feat: registra ventas con multiples items"
git add .
git commit -m "feat: agrega alertas y reportes operativos"
git add .
git commit -m "fix: evita ventas con inventario insuficiente"
git add .
git commit -m "fix: valida estados de lotes y doble cosecha"
git add .
git commit -m "refactor: mejora validaciones y menu"
git add .
git commit -m "docs: documenta ejecucion y reglas de negocio"
```

Para GitHub, crea un repositorio llamado `agrocontrol-cba`, relaciónalo con el repositorio local y publica la rama principal. Después crea un Issue y una rama de mejora para generar un Pull Request.

## Autora
María José Solano Rojas



## Casos de prueba

PF001: registrar dos veces P001 y comprobar que el segundo registro sea rechazado.

PF002: ingresar precio 0 o texto y comprobar que se solicite un valor válido.

PF003: intentar cosechar un lote inexistente.

PF004: cosechar dos veces el mismo lote.

PF005: intentar sacar más unidades de las disponibles.

PF006: realizar una venta válida con stock suficiente.

PF007: realizar una venta con mínimo dos productos.

PF008: cerrar el programa, ejecutarlo nuevamente y comprobar que los datos continúan.

PF009: dejar el stock menor o igual al mínimo y consultar alertas.