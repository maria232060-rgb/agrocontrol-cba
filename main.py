import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ARCHIVOS = {k: DATA_DIR / f"{k}.json" for k in ["productos", "lotes", "movimientos", "ventas"]}
ESTADOS_LOTE = {"EN_PRODUCCION", "COSECHADO", "CANCELADO"}

def cargar_datos():
    datos = {}
    for nombre, ruta in ARCHIVOS.items():
        if ruta.exists():
            try:
                with open(ruta, "r", encoding="utf-8") as a:
                    c = json.load(a)
                    datos[nombre] = c if isinstance(c, list) else []
            except (json.JSONDecodeError, OSError):
                datos[nombre] = []
        else:
            datos[nombre] = []
    return datos

def guardar_datos(datos):
    DATA_DIR.mkdir(exist_ok=True)
    for nombre, ruta in ARCHIVOS.items():
        with open(ruta, "w", encoding="utf-8") as a:
            json.dump(datos[nombre], a, ensure_ascii=False, indent=4)

def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def texto_no_vacio(mensaje):
    while True:
        v = input(mensaje).strip()
        if v: return v
        print("El valor no puede estar vacío.")

def leer_numero(mensaje, tipo=float, minimo=None):
    while True:
        try:
            val_str = input(mensaje).strip().replace(",", ".")
            v = int(val_str) if tipo is int else float(val_str)
            if minimo is not None and v < minimo:
                print(f"Debe ser mayor o igual a {minimo}.")
                continue
            return v
        except ValueError:
            print(f"Ingrese un {'entero' if tipo is int else 'número'} válido.")

def confirmar(mensaje):
    return input(f"{mensaje} (S/N): ").strip().upper() == "S"

def producto_por_codigo(datos, codigo):
    return next((p for p in datos["productos"] if p["codigo"] == codigo.strip().upper()), None)

def lote_por_id(datos, id_lote):
    return next((l for l in datos["lotes"] if l["id_lote"] == id_lote.strip().upper()), None)

def siguiente_id(registros, prefijo):
    mayor = 0
    for r in registros:
        i = str(r.get("id", ""))
        if i.startswith(prefijo) and i[len(prefijo):].isdigit():
            mayor = max(mayor, int(i[len(prefijo):]))
    return f"{prefijo}{mayor + 1:04d}"

def stock_producto(datos, codigo):
    c = codigo.upper()
    return sum(m["cantidad"] if m["tipo"] == "ENTRADA" else -m["cantidad"] 
               for m in datos["movimientos"] if m["producto_codigo"] == c)

def listar_productos(datos, solo_activos=True):
    prods = [p for p in datos["productos"] if not solo_activos or p["activo"]]
    if not prods: return print("No hay productos para mostrar.")
    print("\n" + "=" * 90 + f"\n{'CÓDIGO':<10}{'NOMBRE':<25}{'CATEGORÍA':<18}{'UNIDAD':<12}{'PRECIO':>10}{'STOCK':>8}\n" + "=" * 90)
    for p in prods:
        print(f"{p['codigo']:<10}{p['nombre'][:24]:<25}{p['categoria'][:17]:<18}{p['unidad'][:11]:<12}${p['precio']:>9,.0f}{stock_producto(datos, p['codigo']):>8}")
    print("=" * 90)

def registrar_producto(datos):
    print("\n--- REGISTRAR PRODUCTO ---")
    codigo = texto_no_vacio("Código: ").upper()
    if producto_por_codigo(datos, codigo): return print("Ya existe un producto con ese código.")
    datos["productos"].append({
        "codigo": codigo, "nombre": texto_no_vacio("Nombre: "), "categoria": texto_no_vacio("Categoría: "),
        "unidad": texto_no_vacio("Unidad: "), "precio": leer_numero("Precio: $", float, 0.01),
        "stock_minimo": leer_numero("Stock mínimo: ", int, 0), "activo": True
    })
    guardar_datos(datos)
    print("Producto registrado correctamente.")

def buscar_productos(datos):
    print("\n--- CONSULTAR PRODUCTOS ---")
    t = texto_no_vacio("Código o parte del nombre: ").upper()
    enc = [p for p in datos["productos"] if p["activo"] and (t in p["codigo"] or t in p["nombre"].upper())]
    if not enc: return print("No se encontraron productos activos.")
    for p in enc:
        print(f"{p['codigo']} | {p['nombre']} | {p['categoria']} | ${p['precio']:,.0f} | Stock: {stock_producto(datos, p['codigo'])}")

def actualizar_producto(datos):
    print("\n--- ACTUALIZAR PRODUCTO ---")
    p = producto_por_codigo(datos, texto_no_vacio("Código del producto: ").upper())
    if not p: return print("Producto no encontrado.")
    print("Deje vacío un campo para conservar su valor actual.")
    for campo, txt, t, min_v in [("nombre", "Nombre", str, None), ("categoria", "Categoría", str, None), 
                                 ("unidad", "Unidad", str, None), ("precio", "Precio", float, 0.01), 
                                 ("stock_minimo", "Stock mínimo", int, 0)]:
        val = input(f"{txt} [{p[campo]}]: ").strip()
        if val:
            try:
                p[campo] = t(val.replace(",", ".")) if t in (float, int) else val
            except ValueError: print(f"{txt} inválido. No se actualizó.")
    guardar_datos(datos)
    print("Producto actualizado.")

def desactivar_producto(datos):
    print("\n--- DESACTIVAR PRODUCTO ---")
    p = producto_por_codigo(datos, texto_no_vacio("Código: ").upper())
    if not p: return print("Producto no encontrado.")
    if not p["activo"]: return print("El producto ya está desactivado.")
    p["activo"] = False
    guardar_datos(datos)
    print("Producto desactivado. Su historial se conserva.")

def gestion_productos(datos):
    ops = {"1": lambda: registrar_producto(datos), "2": lambda: listar_productos(datos),
           "3": lambda: buscar_productos(datos), "4": lambda: actualizar_producto(datos),
           "5": lambda: desactivar_producto(datos), "6": lambda: listar_productos(datos, False)}
    while True:
        print("\n--- GESTIÓN DE PRODUCTOS ---\n1. Registrar\n2. Listar activos\n3. Buscar\n4. Actualizar\n5. Desactivar\n6. Ver todos\n0. Volver")
        o = input("Seleccione: ").strip()
        if o == "0": break
        ops.get(o, lambda: print("Opción inválida."))()

def registrar_lote(datos):
    print("\n--- REGISTRAR LOTE ---")
    id_l = texto_no_vacio("ID del lote: ").upper()
    if lote_por_id(datos, id_l): return print("Ese ID de lote ya existe.")
    listar_productos(datos)
    p = producto_por_codigo(datos, texto_no_vacio("Código del producto: ").upper())
    if not p or not p["activo"]: return print("El producto no existe o está desactivado.")
    fecha = texto_no_vacio("Fecha de siembra (AAAA-MM-DD): ")
    try: datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError: return print("Fecha inválida.")
    datos["lotes"].append({"id_lote": id_l, "producto_codigo": p["codigo"], "fecha_siembra": fecha,
                           "area_m2": leer_numero("Área en m²: ", float, 0.01), "cantidad_producida": 0, "estado": "EN_PRODUCCION"})
    guardar_datos(datos)
    print("Lote registrado.")

def listar_lotes(datos):
    print("\n--- LOTES ---")
    if not datos["lotes"]: return print("No hay lotes registrados.")
    for l in datos["lotes"]:
        p = producto_por_codigo(datos, l["producto_codigo"])
        nom = p["nombre"] if p else "Producto histórico"
        print(f"{l['id_lote']} | {nom} ({l['producto_codigo']}) | Siembra: {l['fecha_siembra']} | Área: {l['area_m2']} m² | Producida: {l['cantidad_producida']} | Estado: {l['estado']}")

def cambiar_estado_lote(datos):
    print("\n--- CAMBIAR ESTADO DE LOTE ---")
    l = lote_por_id(datos, texto_no_vacio("ID del lote: ").upper())
    if not l: return print("El lote no existe.")
    print("1. EN_PRODUCCION\n2. COSECHADO\n3. CANCELADO")
    o = input("Nuevo estado: ").strip()
    if o == "1" and l["estado"] == "COSECHADO": return print("Un lote cosechado no puede volver a producción.")
    if o == "2":
        if l["estado"] in ("COSECHADO", "CANCELADO"): return print(f"Estado inválido para cosecha ({l['estado']}).")
        cant = leer_numero("Cantidad producida: ", int, 1)
        l.update({"cantidad_producida": cant, "estado": "COSECHADO"})
        datos["movimientos"].append({"id": siguiente_id(datos["movimientos"], "M"), "producto_codigo": l["producto_codigo"],
                                     "tipo": "ENTRADA", "cantidad": cant, "motivo": f"Cosecha lote {l['id_lote']}", "fecha": ahora()})
        guardar_datos(datos)
        return print("Lote cosechado y entrada de inventario generada automáticamente.")
    if o == "3" and l["estado"] == "COSECHADO": return print("Un lote cosechado no puede cancelarse.")
    estados = {"1": "EN_PRODUCCION", "3": "CANCELADO"}
    if o in estados: l["estado"] = estados[o]
    else: return print("Estado inválido.")
    guardar_datos(datos)
    print("Estado actualizado.")

def gestion_lotes(datos):
    ops = {"1": lambda: registrar_lote(datos), "2": lambda: listar_lotes(datos), "3": lambda: cambiar_estado_lote(datos)}
    while True:
        print("\n--- GESTIÓN DE LOTES ---\n1. Registrar lote\n2. Listar lotes\n3. Cambiar estado / cosechar\n0. Volver")
        o = input("Seleccione: ").strip()
        if o == "0": break
        ops.get(o, lambda: print("Opción inválida."))()

def registrar_movimiento(datos, tipo):
    print(f"\n--- {tipo} DE INVENTARIO ---")
    listar_productos(datos)
    codigo = texto_no_vacio("Código: ").upper()
    p = producto_por_codigo(datos, codigo)
    if not p or not p["activo"]: return print("Producto inexistente o inactivo.")
    cant = leer_numero("Cantidad: ", int, 1)
    if tipo == "SALIDA":
        stk = stock_producto(datos, codigo)
        if cant > stk: return print(f"Stock insuficiente. Disponible: {stk}.")
    datos["movimientos"].append({"id": siguiente_id(datos["movimientos"], "M"), "producto_codigo": codigo,
                                 "tipo": tipo, "cantidad": cant, "motivo": texto_no_vacio("Motivo: "), "fecha": ahora()})
    guardar_datos(datos)
    print(f"{tipo.capitalize()} registrada.")

def listar_movimientos(datos):
    print("\n--- MOVIMIENTOS ---")
    if not datos["movimientos"]: return print("No hay movimientos.")
    for m in datos["movimientos"]:
        print(f"{m['id']} | {m['producto_codigo']} | {m['tipo']} | {m['cantidad']} | {m['motivo']} | {m['fecha']}")

def gestion_inventario(datos):
    ops = {"1": lambda: registrar_movimiento(datos, "ENTRADA"), "2": lambda: registrar_movimiento(datos, "SALIDA"), "3": lambda: listar_movimientos(datos)}
    while True:
        print("\n--- MOVIMIENTOS DE INVENTARIO ---\n1. Registrar entrada\n2. Registrar salida\n3. Listar movimientos\n0. Volver")
        o = input("Seleccione: ").strip()
        if o == "0": break
        ops.get(o, lambda: print("Opción inválida."))()

def registrar_venta(datos):
    print("\n--- REGISTRAR VENTA ---")
    if not any(p["activo"] for p in datos["productos"]): return print("No hay productos activos.")
    items = []
    while True:
        listar_productos(datos)
        codigo = input("Código del producto (ENTER para terminar): ").strip().upper()
        if not codigo: break
        p = producto_por_codigo(datos, codigo)
        if not p or not p["activo"]:
            print("Producto inexistente o inactivo.")
            continue
        cant = leer_numero("Cantidad: ", int, 1)
        ya = next((i for i in items if i["codigo"] == codigo), None)
        cant_tot = cant + (ya["cantidad"] if ya else 0)
        stk = stock_producto(datos, codigo)
        if cant_tot > stk:
            print(f"Stock insuficiente. Disponible: {stk}.")
            continue
        if ya:
            ya["cantidad"] = cant_tot
            ya["subtotal"] = cant_tot * ya["precio_unitario"]
        else:
            items.append({"codigo": codigo, "cantidad": cant, "precio_unitario": p["precio"], "subtotal": cant * p["precio"]})
        if not confirmar("¿Agregar otro producto?"): break

    if not items: return print("La venta debe contener al menos un ítem válido.")
    if any(item["cantidad"] > stock_producto(datos, item["codigo"]) for item in items):
        return print("La venta no puede registrarse porque el stock cambió.")

    total = sum(i["subtotal"] for i in items)
    venta = {"id": siguiente_id(datos["ventas"], "V"), "fecha": ahora(), "items": items, "total": total}
    datos["ventas"].append(venta)
    for i in items:
        datos["movimientos"].append({"id": siguiente_id(datos["movimientos"], "M"), "producto_codigo": i["codigo"],
                                     "tipo": "SALIDA", "cantidad": i["cantidad"], "motivo": f"Venta {venta['id']}", "fecha": ahora()})
    guardar_datos(datos)
    print(f"Venta {venta['id']} registrada. Total: ${total:,.0f}")

def consultar_ventas(datos):
    print("\n--- VENTAS ---")
    if not datos["ventas"]: return print("No hay ventas registradas.")
    for v in datos["ventas"]:
        print(f"\n{v['id']} | {v['fecha']} | Total: ${v['total']:,.0f}")
        for i in v["items"]:
            print(f"  {i['codigo']} x{i['cantidad']} @ ${i['precio_unitario']:,.0f} = ${i['subtotal']:,.0f}")

def alertas_stock(datos):
    print("\n--- ALERTAS DE STOCK ---")
    alertas = [(p, stock_producto(datos, p["codigo"])) for p in datos["productos"] if p["activo"] and stock_producto(datos, p["codigo"]) <= p["stock_minimo"]]
    if not alertas: return print("No hay productos en alerta.")
    for p, stk in alertas:
        print(f"{p['codigo']} | {p['nombre']} | Stock: {stk} | Mínimo: {p['stock_minimo']}")

def reportes(datos):
    print("\n--- REPORTES ---\n\nEXISTENCIAS Y VALOR DEL INVENTARIO")
    val_tot = sum(stock_producto(datos, p["codigo"]) * p["precio"] for p in datos["productos"] if p["activo"])
    for p in datos["productos"]:
        if p["activo"]:
            stk = stock_producto(datos, p["codigo"])
            print(f"{p['codigo']} | {p['nombre']} | Stock: {stk} | Valor: ${stk * p['precio']:,.0f}")
    print(f"Valor total del inventario: ${val_tot:,.0f}")

    uv = sum(i["cantidad"] for v in datos["ventas"] for i in v["items"])
    ing = sum(v["total"] for v in datos["ventas"])
    print(f"\nVENTAS\nNúmero de ventas: {len(datos['ventas'])}\nUnidades vendidas: {uv}\nIngresos acumulados: ${ing:,.0f}")

    cants = {}
    for v in datos["ventas"]:
        for i in v["items"]: cants[i["codigo"]] = cants.get(i["codigo"], 0) + i["cantidad"]
    rk = sorted(cants.items(), key=lambda x: x[1], reverse=True)[:3]
    print("\nTOP 3 PRODUCTOS MÁS VENDIDOS")
    if not rk: print("No hay ventas.")
    else:
        for pos, (cod, cant) in enumerate(rk, 1):
            p = producto_por_codigo(datos, cod)
            print(f"{pos}. {p['nombre'] if p else cod} ({cod}) - {cant} unidades")

    print(f"\nLOTES\nTotal de lotes: {len(datos['lotes'])}")
    for e in ESTADOS_LOTE:
        print(f"{e}: {sum(1 for l in datos['lotes'] if l['estado'] == e)}")

def pruebas_demo():
    print("\nPRUEBAS MÍNIMAS SUGERIDAS\nPF001 Producto duplicado\nPF002 Precio inválido\nPF003 Lote inexistente\nPF004 Doble cosecha\nPF005 Salida excesiva\nPF006 Venta válida\nPF007 Venta múltiple\nPF008 Persistencia\nPF009 Alerta de stock\n\nEjecuta cada caso desde los menús y toma capturas como evidencia.\n")

def menu_principal():
    datos = cargar_datos()
    guardar_datos(datos)
    acciones = {"1": lambda: gestion_productos(datos), "2": lambda: gestion_lotes(datos),
                "3": lambda: gestion_inventario(datos), "4": lambda: registrar_venta(datos),
                "5": lambda: consultar_ventas(datos), "6": lambda: alertas_stock(datos),
                "7": lambda: reportes(datos), "8": lambda: (guardar_datos(datos), print("Datos guardados correctamente.")),
                "9": pruebas_demo}
    while True:
        print("\n==================== AGROCONTROL CBA ====================\n1. Gestión de productos\n2. Gestión de lotes productivos\n3. Movimientos de inventario\n4. Registrar venta\n5. Consultar ventas\n6. Alertas de stock\n7. Reportes\n8. Guardar datos\n9. Ver guía de pruebas\n0. Salir\n==========================================================")
        o = input("Seleccione una opción: ").strip()
        if o == "0":
            guardar_datos(datos)
            print("Datos guardados. Hasta luego.")
            break
        acciones.get(o, lambda: print("Opción inválida. Intente nuevamente."))()

if __name__ == "__main__":
    menu_principal()

