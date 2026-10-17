// Achica las fotos grandes antes de subirlas: cargan más rápido y entran en el límite de
// Vercel (4,5 MB por envío). 2560 px de lado mayor alcanza para ver la obra a pantalla completa.
const LADO_MAXIMO = 2560
const PESO_MAXIMO = 3.5 * 1024 * 1024

export async function prepararImagen(archivo) {
  // Los GIF pueden ser animados: se suben tal cual
  if (archivo.type === 'image/gif') return archivo

  let bitmap
  try {
    bitmap = await createImageBitmap(archivo, { imageOrientation: 'from-image' })
  } catch {
    return archivo // formato que el navegador no puede leer: que lo valide el servidor
  }

  const escala = Math.min(1, LADO_MAXIMO / Math.max(bitmap.width, bitmap.height))
  if (escala === 1 && archivo.size <= PESO_MAXIMO) {
    bitmap.close()
    return archivo
  }

  const canvas = document.createElement('canvas')
  canvas.width = Math.round(bitmap.width * escala)
  canvas.height = Math.round(bitmap.height * escala)
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = '#ffffff' // fondo blanco para imágenes con transparencia
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  bitmap.close()

  let calidad = 0.9
  let blob
  do {
    blob = await new Promise((resolver) => canvas.toBlob(resolver, 'image/jpeg', calidad))
    calidad -= 0.1
  } while (blob && blob.size > PESO_MAXIMO && calidad >= 0.5)

  if (!blob) return archivo
  const nombre = archivo.name.replace(/\.[^.]+$/, '') + '.jpg'
  return new File([blob], nombre, { type: 'image/jpeg' })
}
