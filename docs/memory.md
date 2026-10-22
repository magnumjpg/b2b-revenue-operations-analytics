# Continuous Memory Ledger

## Lessons (Mejora Continua)
- *Regla*: Siempre verificar la ejecución de código antes de dar la tarea por completada. Ejecutar scripts de validación y comprobar que los outputs y métricas numéricas sean 100% coherentes. (Verificado: 6 tests unitarios pasan en 4.61s; pipeline end-to-end corre en 4.71s).
- *Regla*: Nunca tocar ni generar archivos `.env` (seguridad respetada al 100%).
- *Regla*: En proyectos de analítica financiera B2B, mantener trazabilidad total entre el cálculo a nivel de línea de factura y las cifras agregadas en `SYSTEM_NOTES.md` y `README.md`.
- *Regla*: La dualidad "System 1" (Fast reflexive CPQ pricing guardrails & exception approver <0.02ms) y "System 2" (Strategic analytical optimizer, K-Means RFM clustering & portfolio policy simulation) es una arquitectura de altísimo valor que cautiva tanto a hiring managers técnicos como a C-Suite / VPs de Finanzas y Revenue Operations.
- *Regla*: Para curvas de rentabilidad acumulada de Stobachoff (Whale Curve), la modelización de costes logísticos fijos por pedido desproporcionados en micro-pedidos (<5 unidades) combinados con sobre-descuentos comerciales (40-50%) reproduce fielmente la destrucción real de EBITDA en distribución B2B.

## Actualidad (Progreso Activo)
- **Fase 1: Configuración de Arquitectura**: Completada (`docs/context.md`, `docs/memory.md`, estructura de carpetas).
- **Fase 2: Generación de Datos ERP B2B**: Completada (`src/data_generator.py`). Generadas 55,000 líneas de factura en `data/b2b_erp_transactions.parquet` con 800 clientes, 25 comerciales, 4 familias de producto, flete por pedido y coste de financiación WACC 8.5%.
- **Fase 3: Motor Cuantitativo (Waterfall & Whale Curve)**:
  - `src/waterfall_analyzer.py`: Descompone los $1,439.5M de List Price hasta los $210.72M de Pocket EBITDA.
  - `src/whale_curve.py`: Demuestra que el top 20% genera 132.9% del beneficio final, alcanzando un pico de $296.30M (140.6% del beneficio final) en el cliente 678 (84.8%), mientras que la cola del 15% destruye -$85.58M (-40.6% del EBITDA).
- **Fase 4: Motor de Pricing Dual (System 1 vs System 2)**:
  - `src/clustering_guardrails.py`: K-Means en 4 clústeres y auditoría de comerciales rebeldes (`REP-02`, `REP-04`, `REP-05` con descuentos del 47-49% en pedidos pequeños).
  - `src/pricing_engine.py`:
    - *System 1*: Validador heurístico y de reglas en tiempo real (<0.02 ms) para CPQ con bloqueo de micro-pedidos, ajuste de MOQ y techo de descuento.
    - *System 2*: Simulador estratégico que proyecta una recuperación de **+$100.95M de EBITDA (+791 bps / +7.91% de expansión de margen)**.
- **Fase 5: Modelo Financiero Ejecutivo en Excel**:
  - `src/excel_exporter.py`: Generador automático del modelo corporativo de 5 pestañas en `data/B2B_Margin_Leakage_Executive_Model.xlsx`. Estilo minimalista monocromático alineado con el CV del usuario, ancho de columnas generoso sin cortes ni `###`, formato contable nativo con rojo en negativos.
  - Pestañas: `01_Executive_Summary`, `02_Pocket_Margin_Waterfall`, `03_Whale_Curve_Deciles`, `04_Pricing_&_MOQ_Matrix`, `05_Sales_Rep_Audit`.
- **Fase 6: Visualizaciones de Nivel Ejecutivo**:
  - `src/visualizations.py`: Generadas 4 figuras a 300 DPI en `/assets/` (Waterfall, Whale Curve, Price-Volume Dispersion con cuadrante de peligro, y Escenario de Recuperación EBITDA).
- **Fase 7: Testing & Repositorio en Inglés para Remoto USA**:
  - `src/elasticity_engine.py`: Modelo econométrico log-log de elasticidad precio-volumen con Scikit-Learn.
  - `tests/test_pipeline.py`: 8 tests unitarios pasando al 100% en 3.5s.
  - `main.py`: Orquestador principal de pipeline.
  - `SYSTEM_NOTES.md`: Bitácora cuantitativa continua.
  - `notebooks/01_executive_margin_audit.ipynb`: Notebook interactivo ejecutable.
  - `README.md`: Documento de cartera redactado en estilo académico/tesina ejecutiva (prosa conectada con las figuras, cero listas de viñetas genéricas tipo IA, 100% inglés de negocios para EE.UU.).
  - `README_ES.md`: Versión completa espejo en español con el mismo nivel de redacción académica para reclutadores y empresas hispanohablantes, con selector de idioma cruzado.
