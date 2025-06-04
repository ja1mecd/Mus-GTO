#!/usr/bin/env python3
"""
Generador de Base de Datos SQL para Mus
Calcula todas las 330 manos únicas y las almacena en MySQL/MariaDB
"""

# Importaciones - Soporta tanto mysql-connector-python como PyMySQL
try:
    import mysql.connector
    from mysql.connector import Error
    USE_PYMYSQL = False
    print("✅ Usando mysql-connector-python")
except ImportError:
    try:
        import pymysql
        USE_PYMYSQL = True
        print("✅ Usando PyMySQL como alternativa")
        # Configurar PyMySQL para que actúe como MySQLdb
        pymysql.install_as_MySQLdb()
    except ImportError:
        print("❌ Error: Necesitas instalar mysql-connector-python o PyMySQL")
        print("💡 Ejecuta: pip install mysql-connector-python")
        print("💡 O como alternativa: pip install PyMySQL")
        sys.exit(1)

import itertools
from collections import Counter
import time
import sys
from typing import List, Tuple, Dict, Any

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'mus_db',
    'user': 'root',  # Cambiar por tu usuario
    'password': 'jacd2jacd',  # Cambiar por tu contraseña
    'charset': 'utf8mb4'
}

# Baraja de Mus
BARAJA_MUS = [1,1,1,1,1,1,1,1,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,10,10,10,10,11,11,11,11,12,12,12,12,12,12,12,12]

class CalculadoraMus:
    """Clase que contiene todos los cálculos del Mus"""
    
    @staticmethod
    def valor_carta(carta: int) -> int:
        """Devuelve el valor de una carta para los cálculos"""
        return carta if carta < 10 else 10
    
    @staticmethod
    def baraja_sin_mano(baraja: List[int], mano: List[int]) -> List[int]:
        """Quita una mano de la baraja"""
        nueva_baraja = baraja.copy()
        for carta in mano:
            if carta in nueva_baraja:
                nueva_baraja.remove(carta)
        return nueva_baraja
    
    @staticmethod
    def ganar_grande(mano1: List[int], mano2: List[int]) -> int:
        """Determina si mano1 gana a mano2 en Grande"""
        m1 = sorted(mano1, reverse=True)
        m2 = sorted(mano2, reverse=True)
        
        if m1 == m2:
            return 1
        
        for i in range(4):
            if m1[i] > m2[i]:
                return 1
            elif m1[i] < m2[i]:
                return 0
        return 0
    
    @staticmethod
    def ganar_chica(mano1: List[int], mano2: List[int]) -> int:
        """Determina si mano1 gana a mano2 en Chica"""
        m1 = sorted(mano1)
        m2 = sorted(mano2)
        
        if m1 == m2:
            return 1
        
        for i in range(4):
            v1 = CalculadoraMus.valor_carta(m1[i])
            v2 = CalculadoraMus.valor_carta(m2[i])
            if v1 < v2:
                return 1
            elif v1 > v2:
                return 0
        return 0
    
    @staticmethod
    def clasificar_par(mano: List[int]) -> Tuple[int, List[int]]:
        """Clasifica el tipo de par de una mano"""
        conteo = Counter(mano)
        repetidos = {num: veces for num, veces in conteo.items() if veces > 1}
        frecuencias = list(repetidos.values())
        
        if 4 in frecuencias:
            codigo = 3  # Cuaternas
        elif len(frecuencias) == 2:
            codigo = 3  # Duples
        elif 3 in frecuencias:
            codigo = 2  # Medias
        elif 2 in frecuencias:
            codigo = 1  # Pareja
        else:
            codigo = 0  # Sin pares
            
        return codigo, sorted(repetidos.keys(), reverse=True)
    
    @staticmethod
    def ganar_pares(mano1: List[int], mano2: List[int]) -> int:
        """Determina si mano1 gana a mano2 en Pares"""
        clase1 = CalculadoraMus.clasificar_par(mano1)
        clase2 = CalculadoraMus.clasificar_par(mano2)
        
        if clase1[0] > clase2[0]:
            return 1
        elif clase1[0] < clase2[0]:
            return 0
        elif clase1[0] == clase2[0] and clase1[0] != 0:
            # Mismo tipo de par, comparar valores
            if len(clase1[1]) == 2 and len(clase2[1]) == 2:  # Duples
                duples1 = sorted(clase1[1], reverse=True)
                duples2 = sorted(clase2[1], reverse=True)
                if duples1[0] > duples2[0]:
                    return 1
                elif duples1[0] < duples2[0]:
                    return 0
                elif duples1[0] == duples2[0]:
                    return 1 if duples1[1] >= duples2[1] else 0
            
            if clase1[1][0] >= clase2[1][0]:
                return 1
            
        return 0
    
    @staticmethod
    def ganar_juego(mano1: List[int], mano2: List[int]) -> int:
        """Determina si mano1 gana a mano2 en Juego"""
        suma1 = sum(CalculadoraMus.valor_carta(carta) for carta in mano1)
        suma2 = sum(CalculadoraMus.valor_carta(carta) for carta in mano2)
        
        if suma1 > 30 and suma2 > 30:
            if suma1 > 32 and suma2 > 32:
                return 1 if suma1 >= suma2 else 0
            elif suma1 < 33 and suma2 > 32:
                return 1
            elif suma1 < 33 and suma2 < 33:
                return 1 if suma1 <= suma2 else 0
        return 0
    
    @staticmethod
    def ganar_punto(mano1: List[int], mano2: List[int]) -> int:
        """Determina si mano1 gana a mano2 en Punto"""
        suma1 = sum(CalculadoraMus.valor_carta(carta) for carta in mano1)
        suma2 = sum(CalculadoraMus.valor_carta(carta) for carta in mano2)
        
        if suma1 < 31 and suma2 < 31:
            return 1 if suma1 >= suma2 else 0
        return 0
    
    @staticmethod
    def valor_del_par(mano: List[int]) -> int:
        """Calcula el valor en piedras del par"""
        clasificacion = CalculadoraMus.clasificar_par(mano)
        codigo = clasificacion[0]
        pares = clasificacion[1]
        
        if codigo == 0:
            return 0
        elif codigo == 1:
            return 1  # Pareja
        elif codigo == 2:
            return 2  # Medias
        elif codigo == 3:
            if len(pares) == 1:
                return 3  # Cuaternas
            else:
                return 3  # Duples
        return 0
    
    @staticmethod
    def valor_del_juego(mano: List[int]) -> int:
        """Calcula el valor en piedras del juego"""
        suma = sum(CalculadoraMus.valor_carta(carta) for carta in mano)
        
        if suma <= 30:
            return 0
        elif suma == 31:
            return 3
        else:
            return 2

class GeneradorBaseDatos:
    """Clase principal para generar la base de datos"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.conexion = None
        self.cursor = None
        self.calculadora = CalculadoraMus()
    
    def conectar(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            if USE_PYMYSQL:
                import pymysql
                self.conexion = pymysql.connect(
                    host=self.db_config['host'],
                    user=self.db_config['user'],
                    password=self.db_config['password'],
                    database=self.db_config['database'],
                    charset=self.db_config['charset']
                )
                self.cursor = self.conexion.cursor()
            else:
                self.conexion = mysql.connector.connect(**self.db_config)
                self.cursor = self.conexion.cursor()
            
            print("✅ Conexión establecida con la base de datos")
            return True
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            return False
    
    def desconectar(self):
        """Cierra la conexión con la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        print("📊 Conexión cerrada")
    
    def generar_manos_unicas(self) -> List[List[int]]:
        """Genera todas las manos únicas del Mus"""
        print("🔄 Generando manos únicas...")
        manos = []
        
        for mano in itertools.combinations(BARAJA_MUS, 4):
            mano_ordenada = sorted(mano)
            if mano_ordenada not in manos:
                manos.append(mano_ordenada)
        
        print(f"✅ Generadas {len(manos)} manos únicas")
        return manos
    
    def contar_frecuencia_mano(self, mano: List[int], baraja: List[int]) -> int:
        """Cuenta cuántas veces puede aparecer una mano en una baraja"""
        cartas_disponibles = Counter(baraja)
        cartas_necesarias = Counter(mano)
        
        # Verificar si es posible
        for carta, necesarias in cartas_necesarias.items():
            if cartas_disponibles.get(carta, 0) < necesarias:
                return 0
        
        # Calcular combinaciones
        from math import factorial
        
        def combinaciones(n, k):
            return factorial(n) // (factorial(k) * factorial(n - k))
        
        resultado = 1
        for carta, necesarias in cartas_necesarias.items():
            disponibles = cartas_disponibles[carta]
            resultado *= combinaciones(disponibles, necesarias)
        
        return resultado
    
    def obtener_manos_con_frecuencias(self, baraja: List[int]) -> List[Dict]:
        """Obtiene todas las manos posibles con sus frecuencias"""
        manos_unicas = self.generar_manos_unicas()
        manos_validas = []
        
        for mano in manos_unicas:
            frecuencia = self.contar_frecuencia_mano(mano, baraja)
            if frecuencia > 0:
                manos_validas.append({
                    'mano': mano,
                    'frecuencia': frecuencia
                })
        
        return manos_validas
    
    def calcular_probabilidades(self, mano: List[int]) -> List[float]:
        """Calcula las probabilidades de ganar cada lance"""
        prob_ganar_grande = 0
        prob_ganar_chica = 0
        prob_ganar_pares = 0
        prob_ganar_juego = 0
        prob_ganar_punto = 0
        
        total_combinaciones = 0
        total_combinaciones_con_pares = 0
        total_combinaciones_con_juego = 0
        total_combinaciones_con_punto = 0
        
        baraja_sin_mi_mano = self.calculadora.baraja_sin_mano(BARAJA_MUS, mano)
        manos_con_frecuencias = self.obtener_manos_con_frecuencias(baraja_sin_mi_mano)
        
        for i, mano1_info in enumerate(manos_con_frecuencias):
            mano1 = mano1_info['mano']
            frecuencia1 = mano1_info['frecuencia']
            
            baraja_sin_mano1 = self.calculadora.baraja_sin_mano(baraja_sin_mi_mano, mano1)
            
            for j, mano2_info in enumerate(manos_con_frecuencias):
                mano2 = mano2_info['mano']
                frecuencia2 = self.contar_frecuencia_mano(mano2, baraja_sin_mano1)
                
                if frecuencia2 > 0:
                    frecuencia_combo = frecuencia1 * frecuencia2
                    total_combinaciones += frecuencia_combo
                    
                    # Grande y Chica
                    if (self.calculadora.ganar_grande(mano, mano1) == 1 and 
                        self.calculadora.ganar_grande(mano, mano2) == 1):
                        prob_ganar_grande += frecuencia_combo
                    
                    if (self.calculadora.ganar_chica(mano, mano1) == 1 and 
                        self.calculadora.ganar_chica(mano, mano2) == 1):
                        prob_ganar_chica += frecuencia_combo
                    
                    # Pares
                    if (self.calculadora.clasificar_par(mano1)[0] != 0 and 
                        self.calculadora.clasificar_par(mano2)[0] != 0):
                        total_combinaciones_con_pares += frecuencia_combo
                        if (self.calculadora.ganar_pares(mano, mano1) == 1 and 
                            self.calculadora.ganar_pares(mano, mano2) == 1):
                            prob_ganar_pares += frecuencia_combo
                    
                    # Juego
                    suma1 = sum(self.calculadora.valor_carta(carta) for carta in mano1)
                    suma2 = sum(self.calculadora.valor_carta(carta) for carta in mano2)
                    if suma1 > 30 and suma2 > 30:
                        total_combinaciones_con_juego += frecuencia_combo
                        if (self.calculadora.ganar_juego(mano, mano1) == 1 and 
                            self.calculadora.ganar_juego(mano, mano2) == 1):
                            prob_ganar_juego += frecuencia_combo
                    
                    # Punto
                    if suma1 < 31 and suma2 < 31:
                        total_combinaciones_con_punto += frecuencia_combo
                        if (self.calculadora.ganar_punto(mano, mano1) == 1 and 
                            self.calculadora.ganar_punto(mano, mano2) == 1):
                            prob_ganar_punto += frecuencia_combo
        
        # Calcular porcentajes
        return [
            (prob_ganar_grande / total_combinaciones * 100) if total_combinaciones > 0 else 0,
            (prob_ganar_chica / total_combinaciones * 100) if total_combinaciones > 0 else 0,
            (prob_ganar_pares / total_combinaciones_con_pares * 100) if total_combinaciones_con_pares > 0 else 0,
            (prob_ganar_juego / total_combinaciones_con_juego * 100) if total_combinaciones_con_juego > 0 else 0,
            (prob_ganar_punto / total_combinaciones_con_punto * 100) if total_combinaciones_con_punto > 0 else 0
        ]
    
    def calcular_piedras_esperadas(self, mano: List[int], probabilidades: List[float]) -> float:
        """Calcula las piedras esperadas"""
        p_grande = probabilidades[0] / 100
        p_chica = probabilidades[1] / 100
        p_pares = probabilidades[2] / 100
        p_juego = probabilidades[3] / 100
        p_punto = probabilidades[4] / 100
        
        valor_par = self.calculadora.valor_del_par(mano)
        valor_juego = self.calculadora.valor_del_juego(mano)
        
        return (2 * (p_grande + p_chica + p_pares + p_juego + p_punto) + 
                valor_par * p_pares + 
                valor_juego * p_juego + 
                p_punto)
    
    def analizar_mano(self, mano: List[int]) -> Dict[str, Any]:
        """Analiza completamente una mano"""
        clasificacion = self.calculadora.clasificar_par(mano)
        suma = sum(self.calculadora.valor_carta(carta) for carta in mano)
        
        # Determinar tipo de mano
        if clasificacion[0] == 3:
            if len(clasificacion[1]) == 1:
                tipo_mano = f"Cuaternas de {clasificacion[1][0]}s"
            else:
                tipo_mano = f"Duples ({clasificacion[1][0]}s y {clasificacion[1][1]}s)"
        elif clasificacion[0] == 2:
            tipo_mano = f"Medias de {clasificacion[1][0]}s"
        elif clasificacion[0] == 1:
            tipo_mano = f"Pareja de {clasificacion[1][0]}s"
        else:
            tipo_mano = "Sin pares"
        
        # Determinar estado de juego
        if suma > 30:
            if suma == 31:
                estado_juego = "Juego de 31"
            elif suma == 32:
                estado_juego = "Juego de 32"
            else:
                estado_juego = f"Juego de {suma} (bueno)"
        else:
            estado_juego = f"Punto de {suma}"
        
        return {
            'tipo_mano': tipo_mano,
            'estado_juego': estado_juego,
            'suma': suma,
            'valor_par': self.calculadora.valor_del_par(mano),
            'valor_juego': self.calculadora.valor_del_juego(mano)
        }
    
    def generar_base_datos_completa(self):
        """Genera la base de datos completa"""
        print("🚀 Iniciando generación de base de datos...")
        inicio = time.time()
        
        if not self.conectar():
            return False
        
        try:
            # Limpiar tabla existente
            self.cursor.execute("DELETE FROM manos_mus")
            self.conexion.commit()
            print("🗑️ Tabla limpiada")
            
            # Generar manos únicas
            manos_unicas = self.generar_manos_unicas()
            total_manos = len(manos_unicas)
            
            print(f"📊 Procesando {total_manos} manos...")
            
            for i, mano in enumerate(manos_unicas, 1):
                # Progreso
                if i % 25 == 0 or i == total_manos:
                    porcentaje = (i / total_manos) * 100
                    print(f"⚡ Progreso: {i}/{total_manos} ({porcentaje:.1f}%) - Mano: {mano}")
                
                # Calcular todas las estadísticas
                probabilidades = self.calcular_probabilidades(mano)
                piedras_esperadas = self.calcular_piedras_esperadas(mano, probabilidades)
                analisis = self.analizar_mano(mano)
                
                # Crear clave única
                mano_clave = ','.join(map(str, mano))
                
                # Insertar en la base de datos
                query = """
                INSERT INTO manos_mus (
                    carta1, carta2, carta3, carta4, mano_clave,
                    prob_grande, prob_chica, prob_pares, prob_juego, prob_punto,
                    piedras_esperadas, tipo_mano, estado_juego, suma_puntos,
                    valor_par, valor_juego
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                valores = (
                    mano[0], mano[1], mano[2], mano[3], mano_clave,
                    probabilidades[0], probabilidades[1], probabilidades[2], 
                    probabilidades[3], probabilidades[4],
                    piedras_esperadas, analisis['tipo_mano'], analisis['estado_juego'],
                    analisis['suma'], analisis['valor_par'], analisis['valor_juego']
                )
                
                self.cursor.execute(query, valores)
            
            # Confirmar cambios
            self.conexion.commit()
            
            # Calcular estadísticas finales
            self.calcular_estadisticas_globales()
            
            tiempo_total = time.time() - inicio
            print(f"✅ Base de datos generada exitosamente en {tiempo_total:.2f} segundos")
            print(f"📊 Total de manos procesadas: {total_manos}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generando base de datos: {e}")
            self.conexion.rollback()
            return False
        finally:
            self.desconectar()
    
    def calcular_estadisticas_globales(self):
        """Calcula y almacena estadísticas globales"""
        try:
            # Obtener estadísticas
            self.cursor.execute("SELECT COUNT(*) FROM manos_mus")
            total_manos = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT AVG(piedras_esperadas) FROM manos_mus")
            promedio_piedras = self.cursor.fetchone()[0]
            
            self.cursor.execute("""
                SELECT id FROM manos_mus 
                WHERE piedras_esperadas = (SELECT MAX(piedras_esperadas) FROM manos_mus)
                LIMIT 1
            """)
            mejor_mano_id = self.cursor.fetchone()[0]
            
            self.cursor.execute("""
                SELECT id FROM manos_mus 
                WHERE piedras_esperadas = (SELECT MIN(piedras_esperadas) FROM manos_mus)
                LIMIT 1
            """)
            peor_mano_id = self.cursor.fetchone()[0]
            
            # Limpiar estadísticas anteriores
            self.cursor.execute("DELETE FROM estadisticas_mus")
            
            # Insertar nuevas estadísticas
            query_stats = """
            INSERT INTO estadisticas_mus (
                total_manos, mejor_mano_id, peor_mano_id, promedio_piedras
            ) VALUES (%s, %s, %s, %s)
            """
            
            self.cursor.execute(query_stats, (
                total_manos, mejor_mano_id, peor_mano_id, promedio_piedras
            ))
            
            print("📈 Estadísticas globales calculadas")
            
        except Exception as e:
            print(f"⚠️ Error calculando estadísticas: {e}")
    
    def probar_consultas(self):
        """Prueba algunas consultas de ejemplo"""
        if not self.conectar():
            return False
        
        try:
            print("\n🧪 Probando consultas...")
            
            # Probar procedimiento de búsqueda
            print("\n📋 Buscando mano [1,1,7,12]:")
            self.cursor.callproc('BuscarMano', [1, 1, 7, 12])
            for resultado in self.cursor.stored_results():
                filas = resultado.fetchall()
                if filas:
                    for fila in filas:
                        print(f"  Mano: {fila[1]}")
                        print(f"  Tipo: {fila[2]}")
                        print(f"  Estado: {fila[3]}")
                        print(f"  Piedras esperadas: {fila[9]}")
                else:
                    print("  No encontrada")
            
            # Top 5 mejores manos
            print("\n🏆 Top 5 mejores manos:")
            self.cursor.execute("""
                SELECT 
                    CONCAT('[', carta1, ',', carta2, ',', carta3, ',', carta4, ']') as mano,
                    tipo_mano,
                    piedras_esperadas
                FROM manos_mus 
                ORDER BY piedras_esperadas DESC 
                LIMIT 5
            """)
            
            for fila in self.cursor.fetchall():
                print(f"  {fila[0]} - {fila[1]} - {fila[2]:.4f} piedras")
            
            # Estadísticas por tipo
            print("\n📊 Estadísticas por tipo de mano:")
            self.cursor.execute("""
                SELECT 
                    tipo_mano,
                    COUNT(*) as cantidad,
                    AVG(piedras_esperadas) as promedio_piedras
                FROM manos_mus 
                GROUP BY tipo_mano
                ORDER BY promedio_piedras DESC
            """)
            
            for fila in self.cursor.fetchall():
                print(f"  {fila[0]}: {fila[1]} manos, {fila[2]:.4f} piedras promedio")
            
        except Exception as e:
            print(f"❌ Error en pruebas: {e}")
        finally:
            self.desconectar()

def main():
    """Función principal"""
    print("=" * 50)
    print("🎯 GENERADOR DE BASE DE DATOS MUS")
    print("=" * 50)
    
    # Verificar configuración
    print(f"📍 Conectando a: {DB_CONFIG['host']}/{DB_CONFIG['database']}")
    print(f"👤 Usuario: {DB_CONFIG['user']}")
    
    respuesta = input("\n¿Continuar con la generación? (s/n): ").lower()
    if respuesta != 's':
        print("🛑 Operación cancelada")
        return
    
    # Crear generador
    generador = GeneradorBaseDatos(DB_CONFIG)
    
    # Generar base de datos
    if generador.generar_base_datos_completa():
        print("\n✅ ¡Generación completada exitosamente!")
        
        # Preguntar si hacer pruebas
        respuesta = input("\n¿Ejecutar pruebas de consulta? (s/n): ").lower()
        if respuesta == 's':
            generador.probar_consultas()
    else:
        print("\n❌ Error en la generación")

if __name__ == "__main__":
    # Verificar dependencias al final del archivo
    main()