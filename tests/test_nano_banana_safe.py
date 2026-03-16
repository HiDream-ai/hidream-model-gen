#!/usr/bin/env python3
"""
Nano Banana 端口测试 - 防重复提交版本
使用锁文件防止并发执行
"""
import sys
import os
import time

# 锁文件路径
LOCK_FILE = '/tmp/nano_banana_test.lock'
RESULT_FILE = '/tmp/nano_banana_result.txt'

def acquire_lock():
    """获取锁，防止重复执行"""
    if os.path.exists(LOCK_FILE):
        # 检查锁是否过期（超过10分钟）
        lock_time = os.path.getmtime(LOCK_FILE)
        if time.time() - lock_time < 600:  # 10分钟内
            print('❌ 测试已在运行中，请勿重复提交')
            print(f'   锁文件: {LOCK_FILE}')
            print(f'   如确需重新运行，请删除: rm {LOCK_FILE}')
            sys.exit(1)
        else:
            print('⚠️  发现过期锁文件，自动清理')
            os.remove(LOCK_FILE)
    
    # 创建锁文件
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    return True

def release_lock():
    """释放锁"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def cleanup_previous():
    """清理之前的结果文件"""
    if os.path.exists(RESULT_FILE):
        os.remove(RESULT_FILE)

# 主程序
try:
    # 获取锁
    acquire_lock()
    cleanup_previous()
    
    sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
    
    # 加载环境变量
    env_path = '/root/.openclaw/workspace/skills/vivago-ai-skill/.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    from scripts import create_client
    
    print('='*60)
    print('Nano Banana 端口测试')
    print('预估积分: 10')
    print('='*60)
    
    client = create_client()
    
    print('\n🍌 Nano Banana 文生图 - 10积分')
    print('⏳ 预计等待 2-5 分钟 (队列拥堵时可能更长)')
    print('   提示: 设置最大等待时间 30 分钟')
    
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("测试超时 (30分钟)")
    
    # 设置30分钟超时
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1800)  # 30分钟
    
    try:
        result = client.text_to_image(
            prompt='fresh fruit arrangement, high quality',
            port='nano-banana',
            batch_size=1
        )
        
        signal.alarm(0)  # 取消超时
        
        if result:
            msg = f'✅ 成功! 图片ID: {result[0].get("image", "N/A")[:30]}...'
            print(f'\n{msg}')
            with open(RESULT_FILE, 'w') as f:
                f.write(f'SUCCESS: {result[0]}')
        else:
            msg = '❌ 失败: 无结果'
            print(f'\n{msg}')
            with open(RESULT_FILE, 'w') as f:
                f.write('FAILED: No result')
                
    except TimeoutError as e:
        msg = f'⚠️  {e}'
        print(f'\n{msg}')
        with open(RESULT_FILE, 'w') as f:
            f.write(f'TIMEOUT: {e}')
    
    print('='*60)
    print('Nano Banana 测试完成')
    print('='*60)
    
finally:
    # 确保释放锁
    release_lock()
