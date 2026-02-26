import sys
sys.path.insert(0, '.')
try:
    from src.core.api_integration import api_integration
    print('导入成功')
except Exception as e:
    print(f'导入失败: {e}')
    import traceback
    traceback.print_exc()