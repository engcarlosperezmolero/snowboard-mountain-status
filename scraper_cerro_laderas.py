import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import telegram
from io import StringIO
import asyncio
import matplotlib.pyplot as plt


def extraer_datos() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    url = 'https://laderas.com.ar/parte-diario/'
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    df_clima = pd.read_html(StringIO(str(soup.find('table', class_='tabla_clima'))))[0]
    df_pistas = pd.read_html(StringIO(str(soup.find('table', class_='tabla_estado_de_pistas'))))[0]
    df_elevacion = pd.read_html(StringIO(str(soup.find('table', class_='tabla_medios_de_elevacion'))))[0]

    # ordenar pistas por estado y dificultad
    df_pistas = df_pistas.sort_values(by=['Estado', 'Dificultad'], ascending=[True, True])

    # ordenar medio de elevacion por estado
    df_elevacion = df_elevacion.sort_values(by=['Estado'], ascending=True)

    return df_clima, df_pistas, df_elevacion


def resumir_informacion(
        df_clima: pd.DataFrame, df_pistas: pd.DataFrame, df_elevacion: pd.DataFrame
) -> str:
    resumen = "Resumen de la información:\n\n"

    # agregar referencia a pagina del parte del cerro https://laderas.com.ar/parte-diario/
    resumen += "ℹ️ Información obtenida de: https://laderas.com.ar/parte-diario/\n\n"

    # Resumen del clima
    resumen += "🏔️ Clima:\n"
    for index, row in df_clima.iterrows():
        resumen += f"Cota {row['Cota']}: {row['Temp.']}, {row['Viento']}, Nieve: {row['Nieve']}, Visibilidad: {row['Visibilidad']}\n"

    # Resumen de pistas abiertas
    pistas_abiertas = df_pistas[df_pistas['Estado'] == 'ABIERTO']
    resumen += f"\n🏂 Pistas abiertas ({len(pistas_abiertas)}/{len(df_pistas)}): \n"
    for index, row in pistas_abiertas.iterrows():
        resumen += f"{row['Nombre']} ({row['Dificultad']})\n"

    # Resumen de elevación
    elevacion_abierta = df_elevacion[df_elevacion['Estado'] == 'ABIERTO']
    resumen += f"\n🚠 Medios de elevación abiertos ({len(elevacion_abierta)}/{len(df_elevacion)}):\n"
    for index, row in elevacion_abierta.iterrows():
        resumen += f"{row['Nombre']} (Horario: {row['Horario']})\n"

    # resumen de pistas temporalmente cerradas
    pistas_temporalmente_cerradas = df_pistas[df_pistas['Estado'] == 'CERRADO HASTA MEDIODIA']
    resumen += f"\n🕛🏂 Pistas temporalmente cerradas ({len(pistas_temporalmente_cerradas)}/{len(df_pistas)}): \n"
    for index, row in pistas_temporalmente_cerradas.iterrows():
        resumen += f"{row['Nombre']} ({row['Dificultad']})\n"

    # resumen de pistas cerradas
    pistas_cerradas = df_pistas[df_pistas['Estado'] == 'CERRADO']
    resumen += f"\n🚫🏂 Pistas cerradas ({len(pistas_cerradas)}/{len(df_pistas)}): \n"
    for index, row in pistas_cerradas.iterrows():
        resumen += f"{row['Nombre']} ({row['Dificultad']})\n"

    # medio de elvacion cerrados
    elevacion_cerrada = df_elevacion[df_elevacion['Estado'] == 'CERRADO']
    resumen += f"\n🚫🚠 Medios de elevación cerrados ({len(elevacion_cerrada)}/{len(df_elevacion)}):\n"
    for index, row in elevacion_cerrada.iterrows():
        resumen += f"{row['Nombre']} (Horario: {row['Horario']})\n"

    return resumen


def resumir_informacion_html(
        df_clima: pd.DataFrame, df_pistas: pd.DataFrame, df_elevacion: pd.DataFrame
) -> str:
    resumen = "<b>Resumen de la información:</b>\n\n"

    # Agregar referencia a página del parte del cerro
    resumen += 'ℹ️ Información obtenida de: <a href="https://laderas.com.ar/parte-diario/">Laderas - Parte Diario</a>\n\n'

    # Resumen del clima
    resumen += "<b>🏔️ Clima:</b>\n"
    for index, row in df_clima.iterrows():
        resumen += f"Cota {row['Cota']}: {row['Temp.']}, {row['Viento']}, Nieve: {row['Nieve']}, Visibilidad: {row['Visibilidad']}\n"

    # Resumen de pistas abiertas
    pistas_abiertas = df_pistas[df_pistas['Estado'] == 'ABIERTO']
    resumen += f"\n<b>🏂 Pistas abiertas ({len(pistas_abiertas)}/{len(df_pistas)}):</b>\n"
    for index, row in pistas_abiertas.iterrows():
        resumen += f"{row['Nombre']} ({row['Dificultad']})\n"

    # Resumen de elevación
    elevacion_abierta = df_elevacion[df_elevacion['Estado'] == 'ABIERTO']
    resumen += f"\n<b>🚠 Medios de elevación abiertos ({len(elevacion_abierta)}/{len(df_elevacion)}):</b>\n"
    for index, row in elevacion_abierta.iterrows():
        resumen += f"{row['Nombre']} (Horario: {row['Horario']})\n"

    # Resumen de pistas temporalmente cerradas
    pistas_temporalmente_cerradas = df_pistas[df_pistas['Estado'] == 'CERRADO HASTA MEDIODIA']
    resumen += f"\n<b>🕛🏂 Pistas temporalmente cerradas ({len(pistas_temporalmente_cerradas)}/{len(df_pistas)}):</b>\n"
    for index, row in pistas_temporalmente_cerradas.iterrows():
        resumen += f"{row['Nombre']} ({row['Dificultad']})\n"

    # Resumen de pistas cerradas
    pistas_cerradas = df_pistas[df_pistas['Estado'] == 'CERRADO']
    resumen += f"\n<b>🚫🏂 Pistas cerradas ({len(pistas_cerradas)}/{len(df_pistas)}):</b>\n"
    for index, row in pistas_cerradas.iterrows():
        resumen += f"{row['Nombre']} ({row['Dificultad']})\n"

    # Medio de elevación cerrados
    elevacion_cerrada = df_elevacion[df_elevacion['Estado'] == 'CERRADO']
    resumen += f"\n<b>🚫🚠 Medios de elevación cerrados ({len(elevacion_cerrada)}/{len(df_elevacion)}):</b>\n"
    for index, row in elevacion_cerrada.iterrows():
        resumen += f"{row['Nombre']} (Horario: {row['Horario']})\n"

    return resumen



def create_image_from_dataframe(df: pd.DataFrame, tipo: str) -> str:
    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    plt.title(f"Tabla {tipo}", pad=20, fontsize=16, weight='bold')
    # Save the image
    fig.savefig(f"table_{tipo}.png")
    plt.close(fig)


async def enviar_a_telegram(
        resumen: str
) -> None:
    # Configura tu token de Telegram y el chat_id del receptor
    bot_token = os.getenv('TOKEN_TELEGRAM_BOT')
    bot = telegram.Bot(token=bot_token)
    chat_id = os.getenv('CHAT_ID_TELEGRAM')

    async with bot:
        await bot.send_message(chat_id=chat_id, text="📊 Resumen del estado del cerro Laderas:")
        # Enviar el resumen como mensaje de texto
        for tipo in ['clima', 'pistas', 'elevacion']:
            with open(f"table_{tipo}.png", "rb") as file:
                await bot.send_photo(chat_id=chat_id, photo=file)

        await bot.send_message(chat_id=chat_id, text=resumen, parse_mode=telegram.constants.ParseMode.HTML)


if __name__ == '__main__':
    chat_id = os.getenv('CHAT_ID_TELEGRAM')

    # Extraer datos
    df_clima, df_pistas, df_elevacion = extraer_datos()

    informacion = {
        'clima': df_clima,
        'pistas': df_pistas,
        'elevacion': df_elevacion
    }

    # Resumir información
    resumen = resumir_informacion(df_clima, df_pistas, df_elevacion)

    for tipo, df in informacion.items():
        create_image_from_dataframe(df, tipo)

    resumen_html = resumir_informacion_html(df_clima, df_pistas, df_elevacion)

    # Enviar a Telegram
    asyncio.run(enviar_a_telegram(resumen_html))
