import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ARCHIVOS = {
    "productos": DATA_DIR / "productos.json",
    "lotes": DATA_DIR / "lotes.json",
    "movimientos": DATA_DIR / "movimientos.json",
    "ventas": DATA_DIR / "ventas.json",
}

ESTADOS_LOTE = {"EN_PRODUCCION", "COSECHADO", "CANCELADO"}


def cargar_datos():
    datos = {}
    for nombre, ruta in ARCHIVOS.items():
        if ruta.exists():
            try:
                with open(ruta, "r", encoding="utf-8") as archivo:
                    contenido = json.load(archivo)
                    datos[nombre] = contenido if isinstance(contenido, list) else []
            except (json.JSONDecodeError, OSError):
                datos[nombre] = []
        else:
            datos[nombre] = []
    return datos


def guardar_datos(datos):
    DATA_DIR.mkdir(exist_ok=True)
    for nombre, ruta in ARCHIVOS.items():
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos[nombre], archivo, ensure_ascii=False, indent=4)


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def texto_no_vacio(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("El valor no puede estar vacío.")


def leer_entero(mensaje, minimo=None):
    while True:
        try:
            valor = int(input(mensaje).strip())
            if minimo is not None and valor < minimo:
                print(f"Debe ser un valor mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Ingrese un número entero válido.")


def leer_decimal(mensaje, minimo=None):
    while True:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
            if minimo is not None and valor < minimo:
                print(f"Debe ser un valor mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Ingrese un número válido.")


def confirmar(mensaje):
    return input(f"{mensaje} (S/N): ").strip().upper() == "S"


def producto_por_codigo(datos, codigo):
    codigo = codigo.strip().upper()
    return next((p for p in datos["productos"] if p["codigo"] == codigo), None)


def lote_por_id(datos, id_lote):
    id_lote = id_lote.strip().upper()
    return next((l for l in datos["lotes"] if l["id_lote"] == id_lote), None)


def siguiente_id(registros, prefijo):
    mayor = 0
    for registro in registros:
        identificador = str(registro.get("id", ""))
        if identificador.startswith(prefijo):
            try:
                mayor = max(mayor, int(identificador[len(prefijo):]))
            except ValueError:
                pass
    return f"{prefijo}{mayor + 1:04d}"


def stock_producto(datos, codigo):
    codigo = codigo.upper()
    stock = 0
    for movimiento in datos["movimientos"]:
        if movimiento["producto_codigo"] == codigo:
            cantidad = movimiento["cantidad"]
            stock += cantidad if movimiento["tipo"] == "ENTRADA" else -cantidad
    return stock


def listar_productos(datos, solo_activos=True):
    productos = datos["productos"]
    if solo_activos:
        productos = [p for p in productos if p["activo"]]
    if not productos:
        print("No hay productos para mostrar.")
        return
    print("\n" + "=" * 90)
    print(f"{'CÓDIGO':<10}{'NOMBRE':<25}{'CATEGORÍA':<18}{'UNIDAD':<12}{'PRECIO':>10}{'STOCK':>8}")
    print("=" * 90)
    for p in productos:
        print(f"{p['codigo']:<10}{p['nombre'][:24]:<25}{p['categoria'][:17]:<18}"
              f"{p['unidad'][:11]:<12}${p['precio']:>9,.0f}{stock_producto(datos, p['codigo']):>8}")
    print("=" * 90)


def registrar_producto(datos):
    print("\n--- REGISTRAR PRODUCTO ---")
    codigo = texto_no_vacio("Código: ").upper()
    if producto_por_codigo(datos, codigo):
        print("Ya existe un producto con ese código.")
        return
    nombre = texto_no_vacio("Nombre: ")
    categoria = texto_no_vacio("Categoría: ")
    unidad = texto_no_vacio("Unidad: ")
    precio = leer_decimal("Precio: $", 0.01)
    stock_minimo = leer_entero("Stock mínimo: ", 0)

    datos["productos"].append({
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "stock_minimo": stock_minimo,
        "activo": True
    })
    guardar_datos(datos)
    print("Producto registrado correctamente.")


def buscar_productos(datos):
    print("\n--- CONSULTAR PRODUCTOS ---")
    termino = texto_no_vacio("Código o parte del nombre: ").upper()
    encontrados = [
        p for p in datos["productos"]
        if p["activo"] and (termino in p["codigo"] or termino in p["nombre"].upper())
    ]
    if not encontrados:
        print("No se encontraron productos activos.")
        return
    for p in encontrados:
        print(f"{p['codigo']} | {p['nombre']} | {p['categoria']} | "
              f"${p['precio']:,.0f} | Stock: {stock_producto(datos, p['codigo'])}")


def actualizar_producto(datos):
    print("\n--- ACTUALIZAR PRODUCTO ---")
    codigo = texto_no_vacio("Código del producto: ").upper()
    producto = producto_por_codigo(datos, codigo)
    if not producto:
        print("Producto no encontrado.")
        return

    print("Deje vacío un campo para conservar su valor actual.")
    nombre = input(f"Nombre [{producto['nombre']}]: ").strip()
    categoria = input(f"Categoría [{producto['categoria']}]: ").strip()
    unidad = input(f"Unidad [{producto['unidad']}]: ").strip()
    precio_txt = input(f"Precio [{producto['precio']}]: ").strip()
    minimo_txt = input(f"Stock mínimo [{producto['stock_minimo']}]: ").strip()

    if nombre:
        producto["nombre"] = nombre
    if categoria:
        producto["categoria"] = categoria
    if unidad:
        producto["unidad"] = unidad
    if precio_txt:
        try:
            precio = float(precio_txt.replace(",", "."))
            if precio <= 0:
                raise ValueError
            producto["precio"] = precio
        except ValueError:
            print("Precio inválido. No se actualizó ese campo.")
    if minimo_txt:
        try:
            minimo = int(minimo_txt)
            if minimo < 0:
                raise ValueError
            producto["stock_minimo"] = minimo
        except ValueError:
            print("Stock mínimo inválido. No se actualizó ese campo.")

    guardar_datos(datos)
    print("Producto actualizado.")


def desactivar_producto(datos):
    print("\n--- DESACTIVAR PRODUCTO ---")
    codigo = texto_no_vacio("Código: ").upper()
    producto = producto_por_codigo(datos, codigo)
    if not producto:
        print("Producto no encontrado.")
        return
    if not producto["activo"]:
        print("El producto ya está desactivado.")
        return
    producto["activo"] = False
    guardar_datos(datos)
    print("Producto desactivado. Su historial se conserva.")


def gestion_productos(datos):
    while True:
        print("""
--- GESTIÓN DE PRODUCTOS ---
1. Registrar
2. Listar activos
3. Buscar
4. Actualizar
5. Desactivar
6. Ver todos
0. Volver
""")
        opcion = input("Seleccione: ").strip()
        if opcion == "1":
            registrar_producto(datos)
        elif opcion == "2":
            listar_productos(datos)
        elif opcion == "3":
            buscar_productos(datos)
        elif opcion == "4":
            actualizar_producto(datos)
        elif opcion == "5":
            desactivar_producto(datos)
        elif opcion == "6":
            listar_productos(datos, False)
        elif opcion == "0":
            return
        else:
            print("Opción inválida.")


def registrar_lote(datos):
    print("\n--- REGISTRAR LOTE ---")
    id_lote = texto_no_vacio("ID del lote: ").upper()
    if lote_por_id(datos, id_lote):
        print("Ese ID de lote ya existe.")
        return

    listar_productos(datos)
    codigo = texto_no_vacio("Código del producto: ").upper()
    producto = producto_por_codigo(datos, codigo)
    if not producto or not producto["activo"]:
        print("El producto no existe o está desactivado.")
        return

    fecha = texto_no_vacio("Fecha de siembra (AAAA-MM-DD): ")
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        print("Fecha inválida.")
        return

    area = leer_decimal("Área en m²: ", 0.01)

    datos["lotes"].append({
        "id_lote": id_lote,
        "producto_codigo": codigo,
        "fecha_siembra": fecha,
        "area_m2": area,
        "cantidad_producida": 0,
        "estado": "EN_PRODUCCION"
    })
    guardar_datos(datos)
    print("Lote registrado.")


def listar_lotes(datos):
    print("\n--- LOTES ---")
    if not datos["lotes"]:
        print("No hay lotes registrados.")
        return
    for lote in datos["lotes"]:
        producto = producto_por_codigo(datos, lote["producto_codigo"])
        nombre = producto["nombre"] if producto else "Producto histórico"
        print(f"{lote['id_lote']} | {nombre} ({lote['producto_codigo']}) | "
              f"Siembra: {lote['fecha_siembra']} | Área: {lote['area_m2']} m² | "
              f"Producida: {lote['cantidad_producida']} | Estado: {lote['estado']}")


def cambiar_estado_lote(datos):
    print("\n--- CAMBIAR ESTADO DE LOTE ---")
    id_lote = texto_no_vacio("ID del lote: ").upper()
    lote = lote_por_id(datos, id_lote)
    if not lote:
        print("El lote no existe.")
        return

    print("1. EN_PRODUCCION\n2. COSECHADO\n3. CANCELADO")
    opcion = input("Nuevo estado: ").strip()

    if opcion == "1":
        if lote["estado"] == "COSECHADO":
            print("Un lote cosechado no puede volver a producción.")
            return
        lote["estado"] = "EN_PRODUCCION"
    elif opcion == "2":
        if lote["estado"] == "COSECHADO":
            print("El lote ya fue cosechado.")
            return
        if lote["estado"] == "CANCELADO":
            print("Un lote cancelado no puede cosecharse.")
            return
        cantidad = leer_entero("Cantidad producida: ", 1)
        lote["cantidad_producida"] = cantidad
        lote["estado"] = "COSECHADO"
        datos["movimientos"].append({
            "id": siguiente_id(datos["movimientos"], "M"),
            "producto_codigo": lote["producto_codigo"],
            "tipo": "ENTRADA",
            "cantidad": cantidad,
            "motivo": f"Cosecha lote {lote['id_lote']}",
            "fecha": ahora()
        })
        guardar_datos(datos)
        print("Lote cosechado y entrada de inventario generada automáticamente.")
        return
    elif opcion == "3":
        if lote["estado"] == "COSECHADO":
            print("Un lote cosechado no puede cancelarse.")
            return
        lote["estado"] = "CANCELADO"
    else:
        print("Estado inválido.")
        return

    guardar_datos(datos)
    print("Estado actualizado.")


def gestion_lotes(datos):
    while True:
        print("""
--- GESTIÓN DE LOTES ---
1. Registrar lote
2. Listar lotes
3. Cambiar estado / cosechar
0. Volver
""")
        opcion = input("Seleccione: ").strip()
        if opcion == "1":
            registrar_lote(datos)
        elif opcion == "2":
            listar_lotes(datos)
        elif opcion == "3":
            cambiar_estado_lote(datos)
        elif opcion == "0":
            return
        else:
            print("Opción inválida.")


def registrar_entrada(datos):
    print("\n--- ENTRADA DE INVENTARIO ---")
    listar_productos(datos)
    codigo = texto_no_vacio("Código: ").upper()
    producto = producto_por_codigo(datos, codigo)
    if not producto or not producto["activo"]:
        print("Producto inexistente o inactivo.")
        return
    cantidad = leer_entero("Cantidad: ", 1)
    motivo = texto_no_vacio("Motivo: ")

    datos["movimientos"].append({
        "id": siguiente_id(datos["movimientos"], "M"),
        "producto_codigo": codigo,
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": ahora()
    })
    guardar_datos(datos)
    print("Entrada registrada.")


def registrar_salida(datos):
    print("\n--- SALIDA DE INVENTARIO ---")
    listar_productos(datos)
    codigo = texto_no_vacio("Código: ").upper()
    producto = producto_por_codigo(datos, codigo)
    if not producto or not producto["activo"]:
        print("Producto inexistente o inactivo.")
        return
    cantidad = leer_entero("Cantidad: ", 1)
    stock = stock_producto(datos, codigo)
    if cantidad > stock:
        print(f"Stock insuficiente. Disponible: {stock}.")
        return
    motivo = texto_no_vacio("Motivo: ")

    datos["movimientos"].append({
        "id": siguiente_id(datos["movimientos"], "M"),
        "producto_codigo": codigo,
        "tipo": "SALIDA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": ahora()
    })
    guardar_datos(datos)
    print("Salida registrada.")


def listar_movimientos(datos):
    print("\n--- MOVIMIENTOS ---")
    if not datos["movimientos"]:
        print("No hay movimientos.")
        return
    for m in datos["movimientos"]:
        print(f"{m['id']} | {m['producto_codigo']} | {m['tipo']} | "
              f"{m['cantidad']} | {m['motivo']} | {m['fecha']}")


def gestion_inventario(datos):
    while True:
        print("""
--- MOVIMIENTOS DE INVENTARIO ---
1. Registrar entrada
2. Registrar salida
3. Listar movimientos
0. Volver
""")
        opcion = input("Seleccione: ").strip()
        if opcion == "1":
            registrar_entrada(datos)
        elif opcion == "2":
            registrar_salida(datos)
        elif opcion == "3":
            listar_movimientos(datos)
        elif opcion == "0":
            return
        else:
            print("Opción inválida.")



