import bpy

# Import main_panel module
if "bpy" not in locals():
    from . import main_panel
else:
    import importlib
    from . import main_panel  # Thêm dòng này
    importlib.reload(main_panel)

# Định nghĩa danh sách classes để đăng ký
classes = [
    main_panel.PanelBasics,
    main_panel.BTC_PT_BlenderToCascadeurPanel,
    main_panel.BTC_PT_CharacterPanel,
    main_panel.BTC_PT_KeyframeMarkersPanel,
    main_panel.BTC_PT_MarkedKeyframesPanel,
    main_panel.BTC_PT_ExportPanel,
    main_panel.BTC_PT_CascadeurCleanerPanel,
    main_panel.BTC_PT_CascadeurToBlenderPanel,
    main_panel.BTC_UL_KeyframeList,
]