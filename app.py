from shiny import App, ui, render
import pandas as pd
import json

# --- Dados anuais reais (permanecem os mesmos) ---
dados_reais = {
    "created_at": [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
    "vegan": [29984, 35769, 55278, 91523, 139532, 180491, 334789, 736570, 632623, 468847, 396872],
    "vegano": [6714, 9423, 17348, 33360, 60307, 89903, 204458, 393177, 353954, 235771, 208015],
    "vegana": [6168, 8994, 16218, 27314, 39861, 52550, 93595, 297971, 209796, 187781, 159266],
    "vegetariano": [56063, 54464, 52257, 51838, 62452, 73678, 69676, 129261, 129714, 86762, 80583],
    "vegetariana": [41435, 42952, 39694, 48331, 56649, 63730, 68871, 139749, 128235, 94627, 79530],
    "vegane": [38, 58, 120, 274, 156, 182, 165, 764, 1405, 2040, 2547],
    "lactovegetariana": [122, 141, 118, 110, 203, 204, 439, 1256, 1552, 1070, 796],
    "ovolactovegetariana": [104, 116, 85, 95, 181, 182, 403, 1166, 1438, 982, 753],
    "lactovegetariano": [142, 130, 79, 151, 243, 223, 383, 940, 1088, 1112, 434],
    "ovolactovegetariano": [119, 112, 66, 119, 227, 199, 350, 874, 1001, 1053, 404],
    "crudivora": [36, 33, 94, 137, 200, 173, 202, 178, 221, 279, 440],
    "crudivoro": [36, 37, 69, 178, 207, 165, 227, 265, 179, 146, 277],
    "pescetariana": [14, 17, 16, 45, 59, 70, 60, 202, 409, 607, 261],
    "frugivoro": [44, 42, 80, 81, 78, 82, 201, 320, 191, 273, 186],
    "frugivora": [17, 27, 39, 34, 37, 60, 115, 110, 142, 135, 105],
    "flexitariano": [18, 6, 0, 8, 15, 88, 29, 153, 117, 261, 259],
    "flexitariana": [0, 6, 2, 5, 11, 23, 60, 148, 127, 138, 133],
    "ovovegetariano": [2, 3, 6, 7, 5, 12, 9, 35, 40, 48, 24],
    "semivegetariana": [29, 15, 6, 13, 9, 10, 6, 15, 18, 10, 12],
    "ovovegetariana": [2, 2, 2, 3, 7, 7, 9, 33, 34, 34, 25],
    "semivegetariano": [11, 11, 5, 1, 6, 20, 7, 9, 10, 16, 12],
    "piscitariana": [2, 0, 1, 6, 6, 9, 6, 24, 20, 13, 19],
    "piscitariano": [1, 3, 0, 2, 0, 3, 7, 9, 19, 13, 9],
    "pesco-vegetariana": [0, 2, 22, 3, 0, 3, 3, 12, 10, 9, 2],
    "pescovegetariana": [4, 5, 0, 1, 4, 5, 5, 9, 13, 6, 3],
    "pescovegetariano": [1, 2, 0, 0, 1, 7, 6, 3, 12, 6, 3],
    "pesco-vegetariano": [0, 1, 0, 0, 1, 3, 3, 14, 7, 4, 4],
    "apivegetariano": [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
    "apivegetariana": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
}
df_anual = pd.DataFrame(dados_reais)
keywords = [col for col in df_anual.columns if col != "created_at"]

# --- Leitura dos dados mensais a partir de um arquivo Excel ---
# Para ler arquivos .xlsx, você precisa da biblioteca openpyxl.
# Instale-a no seu terminal com: pip install openpyxl
try:
    # ✅ Correção: Use pd.read_excel para ler arquivos do Excel
    df_mensal = pd.read_excel("T01VEGAN_KEYWORDS_TBL_mm.xlsx")
    df_mensal['created_at'] = pd.to_datetime(df_mensal['created_at'])
except FileNotFoundError:
    print("ERRO: Arquivo 'T01VEGAN_KEYWORDS_TBL_mm.xlsx' não encontrado. Verifique se ele está na mesma pasta que o app.py.")
    df_mensal = pd.DataFrame(columns=keywords)
except Exception as e:
    print(f"Ocorreu um erro ao ler o arquivo Excel: {e}")
    df_mensal = pd.DataFrame(columns=keywords)


# --- UI ---
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.script(src="https://code.highcharts.com/highcharts.js")
    ),
    ui.h2("📊 Métricas de Tweets — seleção de palavra-chave e periodicidade"),
    ui.input_radio_buttons(
        "periodicidade",
        "Selecione a periodicidade:",
        {"Anual": "Anual", "Mensal": "Mensal"},
        selected="Anual"
    ),
    ui.input_select(
        "keyword_select",
        "Selecione a palavra-chave:",
        {k: k for k in keywords},
        selected="vegan"
    ),
    ui.output_ui("grafico_html"),
    ui.output_ui("grafico_script"),
)

# --- Server ---
def server(input, output, session):
    @render.ui
    def grafico_html():
        return ui.HTML('<div id="container" style="height: 420px; margin-top:8px;"></div>')

    @render.ui
    def grafico_script():
        kw = input.keyword_select()
        periodicidade = input.periodicidade()

        if periodicidade == "Anual":
            df = df_anual
            x_vals = df["created_at"].astype(str).tolist()
        else:
            df = df_mensal
            if df.empty:
                return ui.tags.script("console.log('Dados mensais não disponíveis');")
            x_vals = df["created_at"].dt.strftime("%Y-%m").tolist()

        cfg = {
            "chart": {"type": "area"},
            "title": {"text": f"Métricas de Tweets para “{kw}” ({periodicidade})"},
            "xAxis": {"categories": x_vals},
            "yAxis": {"title": {"text": "Quantidade"}},
            "tooltip": {
                "shared": True,
                "crosshairs": True,
                "pointFormat": '<span style="color:{series.color}">●</span> {series.name}: <b>{point.y:,.0f}</b><br/>'
            },
            "plotOptions": {
                "area": {"stacking": None, "marker": {"enabled": False, "symbol": "circle"}}
            },
            "legend": {"enabled": False},
            "series": [{
                "name": kw,
                "data": df[kw].tolist() if kw in df.columns else [],
                "color": "#696969",
                "type": "area"
            }],
            "credits": {"enabled": False}
        }

        return ui.tags.script(
            f"""
            (function render() {{
                var go = (typeof Highcharts !== 'undefined') && document.getElementById('container');
                if (!go) {{ setTimeout(render, 50); return; }}
                Highcharts.chart('container', {json.dumps(cfg)});
            }})();
            """
        )

app = App(app_ui, server)