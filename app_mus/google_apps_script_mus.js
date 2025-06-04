/**
 * Google Apps Script - API para Base de Datos Mus
 * 
 * CONFIGURACIÓN INICIAL:
 * 1. Crear un Google Sheet llamado "BaseDatosMus"
 * 2. Importar el CSV generado por Python
 * 3. Pegar este código en script.google.com
 * 4. Implementar como Web App
 */

// ========== CONFIGURACIÓN ==========

// ID de tu Google Sheet (se obtiene de la URL)
const SPREADSHEET_ID = 'TU_SPREADSHEET_ID_AQUI'; // Cambiar por tu ID real

// Nombre de la hoja donde están los datos
const SHEET_NAME = 'Hoja 1';

// ========== FUNCIONES PRINCIPALES ==========

/**
 * Función principal para manejar requests HTTP
 */
function doGet(e) {
  const action = e.parameter.action;
  
  try {
    switch (action) {
      case 'buscar':
        return buscarMano(e.parameter);
      case 'mejores':
        return obtenerMejoresManos(e.parameter);
      case 'estadisticas':
        return obtenerEstadisticas();
      case 'filtrar':
        return filtrarManos(e.parameter);
      case 'test':
        return testConexion();
      default:
        return respuestaJSON({
          success: false,
          error: 'Acción no válida. Usa: buscar, mejores, estadisticas, filtrar, test'
        });
    }
  } catch (error) {
    console.error('Error en doGet:', error);
    return respuestaJSON({
      success: false,
      error: error.toString()
    });
  }
}

/**
 * Función para manejar requests POST
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    if (data.action === 'buscar') {
      return buscarManoPost(data);
    }
    
    return respuestaJSON({
      success: false,
      error: 'Acción POST no válida'
    });
    
  } catch (error) {
    console.error('Error en doPost:', error);
    return respuestaJSON({
      success: false,
      error: error.toString()
    });
  }
}

// ========== FUNCIONES DE BÚSQUEDA ==========

/**
 * Buscar una mano específica
 */
function buscarMano(params) {
  const { carta1, carta2, carta3, carta4 } = params;
  
  if (!carta1 || !carta2 || !carta3 || !carta4) {
    return respuestaJSON({
      success: false,
      error: 'Faltan parámetros: carta1, carta2, carta3, carta4'
    });
  }
  
  // Crear clave ordenada
  const cartas = [
    parseInt(carta1), 
    parseInt(carta2), 
    parseInt(carta3), 
    parseInt(carta4)
  ].sort((a, b) => a - b);
  
  const clave = cartas.join(',');
  
  // Buscar en la hoja
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  const datos = sheet.getDataRange().getValues();
  
  // Buscar la fila correspondiente
  for (let i = 1; i < datos.length; i++) { // Empezar en 1 para saltar headers
    if (datos[i][0] === clave) { // Columna A = mano_clave
      const fila = datos[i];
      
      return respuestaJSON({
        success: true,
        data: {
          mano: [fila[1], fila[2], fila[3], fila[4]], // cartas
          probabilidades: {
            grande: parseFloat(fila[5]),
            chica: parseFloat(fila[6]),
            pares: parseFloat(fila[7]),
            juego: parseFloat(fila[8]),
            punto: parseFloat(fila[9])
          },
          piedrasEsperadas: parseFloat(fila[10]),
          analisis: {
            tipoMano: fila[11],
            estadoJuego: fila[12],
            suma: fila[13],
            valorPar: fila[14],
            valorJuego: fila[15]
          }
        }
      });
    }
  }
  
  return respuestaJSON({
    success: false,
    error: `Mano [${cartas.join(', ')}] no encontrada`
  });
}

/**
 * Buscar mano usando POST
 */
function buscarManoPost(data) {
  return buscarMano(data);
}

/**
 * Obtener las mejores manos
 */
function obtenerMejoresManos(params) {
  const limite = parseInt(params.limite) || 10;
  
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  const datos = sheet.getDataRange().getValues();
  
  // Convertir a objetos y ordenar por piedras esperadas
  const manos = [];
  for (let i = 1; i < datos.length; i++) {
    const fila = datos[i];
    manos.push({
      mano: `[${fila[1]},${fila[2]},${fila[3]},${fila[4]}]`,
      tipoMano: fila[11],
      piedrasEsperadas: parseFloat(fila[10]),
      probabilidades: {
        grande: parseFloat(fila[5]),
        chica: parseFloat(fila[6]),
        pares: parseFloat(fila[7]),
        juego: parseFloat(fila[8]),
        punto: parseFloat(fila[9])
      }
    });
  }
  
  // Ordenar por piedras esperadas (descendente)
  manos.sort((a, b) => b.piedrasEsperadas - a.piedrasEsperadas);
  
  return respuestaJSON({
    success: true,
    data: manos.slice(0, limite)
  });
}

/**
 * Obtener estadísticas globales
 */
function obtenerEstadisticas() {
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  const datos = sheet.getDataRange().getValues();
  
  const piedras = [];
  let mejorMano = null;
  let peorMano = null;
  let maxPiedras = -1;
  let minPiedras = Infinity;
  
  // Analizar datos
  for (let i = 1; i < datos.length; i++) {
    const fila = datos[i];
    const piedrasEsperadas = parseFloat(fila[10]);
    
    piedras.push(piedrasEsperadas);
    
    if (piedrasEsperadas > maxPiedras) {
      maxPiedras = piedrasEsperadas;
      mejorMano = {
        mano: `[${fila[1]},${fila[2]},${fila[3]},${fila[4]}]`,
        tipoMano: fila[11],
        piedrasEsperadas: piedrasEsperadas
      };
    }
    
    if (piedrasEsperadas < minPiedras) {
      minPiedras = piedrasEsperadas;
      peorMano = {
        mano: `[${fila[1]},${fila[2]},${fila[3]},${fila[4]}]`,
        tipoMano: fila[11],
        piedrasEsperadas: piedrasEsperadas
      };
    }
  }
  
  const promedio = piedras.reduce((a, b) => a + b, 0) / piedras.length;
  
  return respuestaJSON({
    success: true,
    data: {
      totalManos: piedras.length,
      promedioPiedras: promedio,
      maxPiedras: maxPiedras,
      minPiedras: minPiedras,
      mejorMano: mejorMano,
      peorMano: peorMano
    }
  });
}

/**
 * Filtrar manos por criterios
 */
function filtrarManos(params) {
  const { tipo, piedrasMin, piedrasMax, limite } = params;
  const limiteFinal = parseInt(limite) || 50;
  
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  const datos = sheet.getDataRange().getValues();
  
  const manosFiltradas = [];
  
  for (let i = 1; i < datos.length; i++) {
    const fila = datos[i];
    const tipoMano = fila[11];
    const piedrasEsperadas = parseFloat(fila[10]);
    
    // Aplicar filtros
    let cumpleFiltros = true;
    
    if (tipo && !tipoMano.toLowerCase().includes(tipo.toLowerCase())) {
      cumpleFiltros = false;
    }
    
    if (piedrasMin && piedrasEsperadas < parseFloat(piedrasMin)) {
      cumpleFiltros = false;
    }
    
    if (piedrasMax && piedrasEsperadas > parseFloat(piedrasMax)) {
      cumpleFiltros = false;
    }
    
    if (cumpleFiltros) {
      manosFiltradas.push({
        mano: `[${fila[1]},${fila[2]},${fila[3]},${fila[4]}]`,
        tipoMano: tipoMano,
        piedrasEsperadas: piedrasEsperadas,
        estadoJuego: fila[12]
      });
    }
  }
  
  // Ordenar por piedras esperadas
  manosFiltradas.sort((a, b) => b.piedrasEsperadas - a.piedrasEsperadas);
  
  return respuestaJSON({
    success: true,
    data: {
      total: manosFiltradas.length,
      manos: manosFiltradas.slice(0, limiteFinal)
    }
  });
}

/**
 * Test de conexión
 */
function testConexion() {
  try {
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
    const ultimaFila = sheet.getLastRow();
    
    return respuestaJSON({
      success: true,
      data: {
        mensaje: 'Conexión exitosa con Google Sheets',
        totalFilas: ultimaFila - 1, // -1 por el header
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    return respuestaJSON({
      success: false,
      error: 'Error conectando con Google Sheets: ' + error.toString()
    });
  }
}

// ========== FUNCIONES AUXILIARES ==========

/**
 * Crear respuesta JSON
 */
function respuestaJSON(objeto) {
  return ContentService
    .createTextOutput(JSON.stringify(objeto))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Función para probar desde el editor (opcional)
 */
function probarAPI() {
  // Probar búsqueda
  const resultadoBuscar = buscarMano({
    carta1: '1',
    carta2: '1', 
    carta3: '7',
    carta4: '12'
  });
  
  console.log('Resultado búsqueda:', JSON.parse(resultadoBuscar.getContent()));
  
  // Probar estadísticas
  const resultadoStats = obtenerEstadisticas();
  console.log('Estadísticas:', JSON.parse(resultadoStats.getContent()));
}

/**
 * Función para configuración inicial
 */
function configuracionInicial() {
  console.log('=== CONFIGURACIÓN INICIAL ===');
  console.log('1. Crear Google Sheet llamado "BaseDatosMus"');
  console.log('2. Importar CSV con los datos');
  console.log('3. Obtener el ID del Sheet de la URL');
  console.log('4. Reemplazar SPREADSHEET_ID en este script');
  console.log('5. Implementar como Web App');
  console.log('6. Permitir acceso a "Anyone" para uso público');
}

// ========== FUNCIONES PARA SHEETS ==========

/**
 * Función para importar datos directamente (alternativa al CSV)
 */
function importarDatosDirectamente() {
  // Esta función se podría usar para importar datos desde MySQL
  // directamente a Google Sheets usando UrlFetchApp
  // Pero requiere un endpoint MySQL público
  
  console.log('Para importar datos, usa el script Python para generar CSV');
  console.log('Luego importa el CSV manualmente a Google Sheets');
}

/**
 * Crear índice para búsquedas más rápidas (opcional)
 */
function crearIndice() {
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  
  // Ordenar por mano_clave para búsquedas más rápidas
  const rango = sheet.getDataRange();
  rango.sort(1); // Ordenar por la primera columna (mano_clave)
  
  console.log('Índice creado - datos ordenados por mano_clave');
}

/**
 * Función de mantenimiento
 */
function mantenimiento() {
  console.log('=== MANTENIMIENTO ===');
  
  try {
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
    const ultimaFila = sheet.getLastRow();
    const ultimaColumna = sheet.getLastColumn();
    
    console.log(`Total de filas: ${ultimaFila}`);
    console.log(`Total de columnas: ${ultimaColumna}`);
    console.log(`Total de manos: ${ultimaFila - 1}`);
    
    // Verificar estructura de datos
    const headers = sheet.getRange(1, 1, 1, ultimaColumna).getValues()[0];
    console.log('Headers:', headers);
    
  } catch (error) {
    console.error('Error en mantenimiento:', error);
  }
}