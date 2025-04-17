/**
 * 修复购物车中图片URL的脚本
 * 在浏览器控制台中运行此脚本以修复现有购物车中的图片问题
 */
(function() {
  console.log('开始执行购物车修复脚本...');
  
  // 从localStorage中获取购物车数据
  const cartData = localStorage.getItem('cart');
  if (!cartData) {
    console.log('购物车为空，无需修复');
    return;
  }

  try {
    // 解析购物车数据
    const cart = JSON.parse(cartData);
    
    // 检查购物车是否为数组
    if (!Array.isArray(cart)) {
      console.error('购物车数据格式错误');
      return;
    }
    
    console.log('购物车修复前数据:', JSON.stringify(cart));
    
    // 修复每一项的图片URL
    let isFixed = false;
    cart.forEach(item => {
      // 检查image_url是否为空、undefined、null或字符串"null"/"undefined"
      if (!item.image_url || item.image_url === 'null' || item.image_url === 'undefined') {
        item.image_url = require('@/assets/default-product.png');
        isFixed = true;
        console.log(`已修复商品 "${item.name}" 的图片URL`);
      }
      
      // 确保数量是正整数
      if (!item.quantity || item.quantity < 1) {
        item.quantity = 1;
        isFixed = true;
        console.log(`已修复商品 "${item.name}" 的数量`);
      }
    });
    
    // 保存修复后的数据
    if (isFixed) {
      localStorage.setItem('cart', JSON.stringify(cart));
      console.log('购物车数据已修复并保存');
      console.log('购物车修复后数据:', JSON.stringify(cart));
    } else {
      console.log('购物车数据无需修复');
    }
    
    return {
      success: true,
      message: isFixed ? '购物车数据已修复' : '购物车数据无需修复',
      data: cart
    };
  } catch (error) {
    console.error('修复购物车数据时出错:', error);
    return {
      success: false,
      message: '修复购物车数据时出错',
      error: error.message
    };
  }
})();
