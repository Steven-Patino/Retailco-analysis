import csv
from pathlib import Path

archivo_csv = Path(__file__).parent.parent / "data" / "Amazon Sale Report.csv"

# NÚMERAL UNO: VENTAS TOTALES CON PYTHON PURO
def ventas_totales(ruta):
    valores = []
    
    with open(ruta, mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)    
        for fila in lector:
            raw_val = fila.get("Amount")
            if raw_val:
                try:
                    valores.append(float(raw_val))
                except ValueError:
                    continue 

    if valores:
        total = sum(valores)
        
        print(f"--- Análisis Final ---")
        print(f"Total de ventas: ${total:,.2f}")
        print(f"Registros procesados: {len(valores)}")
    else:
        print("No se encontraron valores numéricos para procesar.")


#NÚMERAL DOS: FILTRAR LOS 5 PRODUCTOS MÁS VENDIDOS.
def top_productos_vendidos(ruta):
    with open(ruta, mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        ventas_por_sku = {}
        for fila in lector:
            sku = fila.get("SKU")
            cantidad_str = fila.get("Qty")
            
            if sku and cantidad_str and cantidad_str.isdigit():
                cantidad = int(cantidad_str)
                
                ventas_por_sku[sku] = ventas_por_sku.get(sku, 0) + cantidad

    sku_mas_vendidos = sorted(ventas_por_sku.items(), key=lambda item: item[1], reverse=True)

    print(f"{'SKU':<20} | {'Cantidad Vendida'}")
    print("-" * 40)
    for sku, cantidad in sku_mas_vendidos[:5]:
        print(f"{sku:<20} | {cantidad}")


#NÚMERAL 3: NUEVO ARCHIVO CSV CON MENOS CULUMNAS
def crear_csv_reducido(ruta, nueva_ruta):
    columnas_deseadas = ["Order ID", "SKU", "Amount", "Qty"]
    
    with open(ruta, mode='r', encoding='utf-8') as archivo_entrada:
        lector = csv.DictReader(archivo_entrada)
        
        with open(nueva_ruta, mode='w', encoding='utf-8', newline='') as archivo_salida:
            escritor = csv.DictWriter(archivo_salida, fieldnames=columnas_deseadas)
            escritor.writeheader()
            
            for fila in lector:
                nueva_fila = {col: fila[col] for col in columnas_deseadas if col in fila}
                escritor.writerow(nueva_fila)

    print(f"Archivo CSV reducido creado en: {nueva_ruta}")

print("-"*20 + "Resultados" + "-"*20+"\n")
ventas_totales(archivo_csv)
print("\n")
top_productos_vendidos(archivo_csv)
print("\n")
crear_csv_reducido(archivo_csv, Path(__file__).parent.parent / "outputs" / "Ordenes_filtradas.csv")