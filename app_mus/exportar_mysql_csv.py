#!/usr/bin/env python3
"""
Exportar datos de MySQL a CSV para importar en Google Sheets
"""

import mysql.connector
import csv
import sys

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'mus_db',
    'user': 'mus_user',
    'password': 'mus_password',
    'charset': 'utf8mb4'
}

def exportar_mysql_a_csv():
    """Exporta toda la base de datos MySQL a CSV"""
    try:
        # Conectar a MySQL
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        
        print("✅ Conectado a MySQL")
        
        # Obtener todos los datos
        cursor.execute("""
            SELECT 
                mano_clave,
                carta1, carta2, carta3, carta4,
                prob_grande, prob_chica, prob_pares, prob_juego, prob_punto,
                piedras_esperadas,
                tipo_mano, estado_juego, suma_puntos, valor_par, valor_juego
            FROM manos_mus 
            ORDER BY mano_clave
        """)
        
        datos = cursor.fetchall()
        
        # Crear archivo CSV
        with open('manos_mus_google_sheets.csv', 'w', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.writer(archivo_csv)
            
            # Escribir encabezados
            writer.writerow([
                'mano_clave', 'carta1', 'carta2', 'carta3', 'carta4',
                'prob_grande', 'prob_chica', 'prob_pares', 'prob_juego', 'prob_punto',
                'piedras_esperadas', 'tipo_mano', 'estado_juego', 'suma_puntos', 
                'valor_par', 'valor_juego'
            ])
            
            # Escribir datos
            for fila in datos:
                writer.writerow(fila)
        
        print(f"✅ Exportado {len(datos)} manos a 'manos_mus_google_sheets.csv'")
        print("📋 Siguiente paso: Importar este CSV a Google Sheets")
        
        cursor.close()
        conexion.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    exportar_mysql_a_csv()