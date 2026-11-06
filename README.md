# Galería de Arte Virtual · Colegio Privado San Marcos

Galería web para exhibir las obras realizadas por estudiantes. Cada obra se publica con su imagen y su **epígrafe**: nombre y apellido del autor, título, año, técnica y colegio.

La página se puede usar desde computadoras, tablets y celulares, y respeta los colores institucionales: bordó, azul y blanco.

---

## Perfiles de usuario

| Perfil | Quién es | Qué puede hacer |
|---|---|---|
| **Visitante** | Cualquier persona que entra a la página, sin cuenta | Recorrer la galería, buscar y filtrar obras, verlas en grande |
| **Invitado** | Persona que creó su cuenta desde la página, indicando su colegio | Todo lo del visitante, y además subir obras de su colegio y editar o borrar **solo las obras de su colegio** |
| **Administrador** | Cuentas definidas por el colegio | Subir, editar y borrar obras de **cualquier colegio**, y gestionar los usuarios |

Los administradores no se crean desde la página: los define el colegio. Una cuenta creada desde el formulario de registro siempre es de **invitado**.

---

## Funcionalidades

### Galería

- **Portada** con la cantidad de obras, artistas y técnicas publicadas, y un collage con las últimas obras subidas.
- **Mosaico de obras**: cada obra muestra su imagen, título, autor y colegio. Al pasar el mouse aparecen la técnica y el año.
- **Buscador**: busca por nombre o apellido del artista, título, técnica o colegio.
- **Filtros**:
  - por técnica, con botones que se activan con un toque;
  - por colegio y por año, con listas desplegables.
- **Contador** de obras encontradas y botón para limpiar los filtros.

### Proceso de obra

- Sección pública para buscar artistas y ver juntas todas las obras que tengan el mismo nombre de autor.
- Las imágenes de proceso de todas las obras de cada artista se reúnen en una galería, identificadas por título y año de la obra.
- Los usuarios habilitados con permiso sobre el colegio pueden cargar hasta 12 imágenes de proceso por obra, con una descripción opcional. Se aceptan imágenes JPG, PNG, WEBP o GIF.

### Visor de obras

Al tocar una obra se abre en pantalla completa:

- **Imagen en grande** con la ficha completa: título, autor, año, técnica y colegio.
- **Navegación** entre obras:
  - con las flechas de la pantalla o del teclado;
  - en el celular, deslizando el dedo.
- **Ver original**, para abrir la imagen en su tamaño completo.
- **Editar** y **Borrar**, que solo aparecen si el usuario tiene permiso sobre esa obra. Borrar pide confirmación.

### Crear cuenta e ingresar

- **Registro**: nombre y apellido, email, **colegio** y contraseña.
  - El campo colegio sugiere los colegios ya cargados, para que las obras de un mismo colegio queden agrupadas.
  - Al crear la cuenta se ingresa directamente y ya se pueden subir obras.
- **Ingreso** con email y contraseña. La sesión queda abierta en ese dispositivo hasta tocar **Salir**.
- En el encabezado se muestran el nombre del usuario y su colegio, o "Administrador/a".

### Subir una obra

Formulario disponible desde el botón **Subir obra**:

- **Imagen**:
  - Se arrastra al recuadro o se elige desde el dispositivo. En el celular también se puede sacar una foto en el momento.
  - Formatos aceptados: JPG, PNG, WEBP o GIF, de hasta 15 MB.
- **Epígrafe**:
  - nombre y apellido del autor (obligatorios);
  - título (opcional);
  - año y técnica (obligatorios). La técnica tiene sugerencias: acuarela, óleo, témpera, collage, fotografía, etc.;
  - colegio:
    - **para los invitados** se completa solo con el colegio de su perfil y no se puede cambiar;
    - **para los administradores** se puede elegir libremente.
- **Vista previa** de la imagen y de cómo se va a ver el epígrafe antes de publicar.

### Editar y borrar obras

- **Editar** permite corregir cualquier dato del epígrafe y, si hace falta, reemplazar la imagen.
- **Borrar** elimina la obra y su imagen de forma definitiva.
- Un invitado **no puede** editar ni borrar obras de otros colegios. Los botones no aparecen, y el sistema rechaza el intento aunque se acceda por otro camino.

### Gestión de usuarios (solo administradores)

Sección **Usuarios**, con la lista de todas las cuentas:

- nombre, email, rol (Administrador o Invitado), colegio y fecha de alta;
- **cambiar el colegio** de un invitado, por ejemplo para corregir un nombre mal escrito;
- **activar o desactivar** una cuenta: un invitado desactivado puede ingresar, pero no puede subir, editar ni borrar obras;
- **eliminar** la cuenta de un invitado. Las obras que subió se conservan;
- un resumen con la cantidad de invitados y de cuentas sin permisos.

---

## Almacenamiento de las imágenes

- Cada imagen se guarda en el servidor en dos versiones:
  - el **original**, que es el que se abre con "Ver original";
  - una **versión optimizada** más liviana, para que la galería cargue rápido en el celular.
- Antes de guardarla, el sistema verifica que el archivo sea realmente una imagen.
- Todas las obras publicadas son visibles para cualquier persona que entre a la página.
