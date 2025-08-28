from shiny import App, ui, render
import pandas as pd
import json

# --- 1. DEFINIÇÃO DOS NOMES DOS ARQUIVOS JSON (ATUALIZADO) ---
file_anual = "anual_json.json"
file_mensal = "mensal_json.json"

# --- 2. LEITURA DOS DADOS A PARTIR DOS ARQUIVOS JSON ---
try:
    # Use pd.read_json com orient="records" para ler a lista de dicionários
    df_anual = pd.read_json(file_anual, orient="records")
except Exception as e:
    print(f"ERRO: Não foi possível carregar o arquivo '{file_anual}'. Erro: {e}")
    df_anual = pd.DataFrame()

try:
    df_mensal = pd.read_json(file_mensal, orient="records")
    if "created_at" in df_mensal.columns:
        df_mensal["created_at"] = pd.to_datetime(df_mensal["created_at"])
except Exception as e:
    print(f"ERRO: Não foi possível carregar o arquivo '{file_mensal}'. Erro: {e}")
    df_mensal = pd.DataFrame()

# --- 3. KEYWORDS ---
keywords = []
if not df_anual.empty:
    # Garante que a coluna 'created_at' não entre na lista de keywords
    keywords = [col for col in df_anual.columns if col != "created_at"]
    keywords.sort()

# --- UI ---
app_ui = ui.page_sidebar(
    ui.sidebar(
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
        title="Métricas de Tweets",
        collapsible=True,
        collapsed=False,
    ),
    ui.tags.head(
        ui.tags.script(src="https://code.highcharts.com/highcharts.js")
    ),
    ui.card(
        ui.output_ui("grafico_html"),
        ui.output_ui("grafico_script"),
    ),
    title="Análise de Métricas de Tweets",
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
        
        if not kw:
            return

        if periodicidade == "Anual":
            if df_anual.empty:
                return ui.tags.script("console.log('Dados anuais não disponíveis');")
            df = df_anual
            x_vals = df["created_at"].astype(str).tolist()
        else: # Mensal
            if df_mensal.empty:
                return ui.tags.script("console.log('Dados mensais não disponíveis');")
            df = df_mensal
            x_vals = df["created_at"].dt.strftime("%Y-%m").tolist()
        
        series_data = df[kw].tolist() if kw in df.columns else []

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
                "data": series_data,
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