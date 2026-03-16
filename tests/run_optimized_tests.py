#!/usr/bin/env python3
"""
优化后的测试运行器
支持图片流水线测试和视频单独测试
"""
import sys
import os
import subprocess
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / '..'))

from fixtures.cache_manager import get_cache_manager


class OptimizedTestRunner:
    """优化后的测试运行器"""
    
    def __init__(self):
        self.tests_dir = Path(__file__).parent
        self.cache = get_cache_manager()
    
    def show_menu(self):
        """显示测试菜单"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║              Vivago AI Skill - 优化测试方案                  ║
╠══════════════════════════════════════════════════════════════╣
║  图片功能 (流水线测试 - 可顺序执行)                           ║
║  ─────────────────────────────────                           ║
║  1. Tier 3 - 图片功能测试 (16积分)                           ║
║     python tests/test_tier3_image.py                         ║
║                                                                ║
║  2. Tier 4 - 图片端口测试 (20积分)                           ║
║     python tests/test_tier4_image_ports.py                   ║
║                                                                ║
║  视频功能 (必须单独运行 - 避免超时)                           ║
║  ─────────────────────────────────                           ║
║  3. 图生视频 (v3L) - 20积分                                  ║
║     python tests/video_img2vid.py                            ║
║                                                                ║
║  4. 文生视频 (v3L) - 20积分                                  ║
║     python tests/video_txt2vid.py                            ║
║                                                                ║
║  5. 视频首尾帧 (v3L) - 20积分                               ║
║     python tests/video_keyframe.py                           ║
║                                                                ║
║  6. 视频模板 - 30积分                                        ║
║     python tests/video_template.py                           ║
║                                                                ║
║  7. Tier 4 v3L 视频端口 (60积分)                            ║
║     python tests/tier4_video_v3l.py                          ║
║                                                                ║
║  8. Tier 4 Kling video (80积分) - 高积分                    ║
║     python tests/tier4_video_kling.py                        ║
║                                                                ║
║  Tier 5 - 模板测试 (每个30积分，单独文件)                    ║
║  ─────────────────────────────────                           ║
║  9. 生成模板测试文件                                         ║
║     python tests/generate_tier5_tests.py                     ║
║                                                                ║
║  10. 运行单个模板测试                                        ║
║     python tests/tier5_templates/test_template_ghibli.py     ║
║                                                                ║
║  工具                                                        ║
║  ─────────────────────────────────                           ║
║  s. 显示测试状态                                             ║
║  c. 清除缓存                                                 ║
║  q. 退出                                                     ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def run_test(self, command, description):
        """运行测试"""
        print(f'\n{"="*60}')
        print(f'🧪 {description}')
        print(f'{"="*60}\n')
        
        try:
            result = subprocess.run(command, shell=True, cwd=self.tests_dir)
            return result.returncode == 0
        except Exception as e:
            print(f'❌ 运行失败: {e}')
            return False
    
    def show_status(self):
        """显示测试状态"""
        print('\n📊 测试状态:')
        print('-' * 60)
        
        # 图片测试
        image_tests = ['tier3_text_to_image', 'tier3_image_to_image']
        print('\n🖼️  图片功能:')
        for test in image_tests:
            result = self.cache.get_test_result(test)
            status = '✅' if result and result.get('status') == 'success' else '❌'
            print(f'   {status} {test}')
        
        # 视频测试
        video_tests = ['video_img2vid', 'video_txt2vid', 'video_keyframe', 'video_template']
        print('\n🎬 视频功能:')
        for test in video_tests:
            result = self.cache.get_test_result(test)
            status = '✅' if result and result.get('status') == 'success' else '❌'
            print(f'   {status} {test}')
        
        # 端口测试
        print('\n🔌 端口测试:')
        port_tests = ['port_kling_image', 'port_hidream', 'port_nano_banana',
                      'port_v3l_img2vid', 'port_v3l_txt2vid']
        for test in port_tests:
            result = self.cache.get_test_result(test)
            status = '✅' if result and result.get('status') == 'success' else '❌'
            print(f'   {status} {test}')
        
        print('\n' + '-' * 60)
    
    def clear_cache_menu(self):
        """清除缓存菜单"""
        print("""
🗑️  清除缓存:
   1. 清除图片UUID缓存
   2. 清除测试结果缓存
   3. 清除失败记录
   4. 清除所有缓存
   0. 取消
        """)
        
        choice = input('选择: ')
        
        if choice == '1':
            self.cache.clear_image_uuids()
            print('✅ 图片UUID缓存已清除')
        elif choice == '2':
            self.cache.clear_test_results()
            print('✅ 测试结果缓存已清除')
        elif choice == '3':
            self.cache.clear_all_failures()
            print('✅ 失败记录已清除')
        elif choice == '4':
            self.cache.clear_all_cache()
            print('✅ 所有缓存已清除')
        else:
            print('已取消')
    
    def run(self):
        """运行交互式菜单"""
        while True:
            self.show_menu()
            choice = input('\n选择: ').strip().lower()
            
            if choice == '1':
                self.run_test('python3 test_tier3_image.py -v', 'Tier 3 - 图片功能测试')
            
            elif choice == '2':
                self.run_test('python3 test_tier4_image_ports.py -v', 'Tier 4 - 图片端口测试')
            
            elif choice == '3':
                self.run_test('python3 video_img2vid.py', '图生视频测试')
            
            elif choice == '4':
                self.run_test('python3 video_txt2vid.py', '文生视频测试')
            
            elif choice == '5':
                self.run_test('python3 video_keyframe.py', '视频首尾帧测试')
            
            elif choice == '6':
                self.run_test('python3 video_template.py', '视频模板测试')
            
            elif choice == '7':
                self.run_test('python3 tier4_video_v3l.py', 'Tier 4 v3L 视频端口')
            
            elif choice == '8':
                self.run_test('python3 tier4_video_kling.py', 'Tier 4 Kling video 端口')
            
            elif choice == '9':
                self.run_test('python3 generate_tier5_tests.py', '生成Tier 5模板测试')
            
            elif choice == '10':
                template = input('输入模板ID (如 ghibli): ').strip()
                test_file = f'tier5_templates/test_template_{template}.py'
                if Path(self.tests_dir / test_file).exists():
                    self.run_test(f'python3 {test_file}', f'模板 {template} 测试')
                else:
                    print(f'❌ 测试文件不存在: {test_file}')
                    print('   请先运行选项 9 生成测试文件')
            
            elif choice == 's':
                self.show_status()
            
            elif choice == 'c':
                self.clear_cache_menu()
            
            elif choice == 'q':
                print('再见!')
                break
            
            else:
                print('无效选择')
            
            input('\n按回车继续...')


if __name__ == '__main__':
    runner = OptimizedTestRunner()
    runner.run()
