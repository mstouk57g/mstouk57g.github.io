// 全局变量
let config = {};
let isFirstLoad = true;

// DOM元素引用
const elements = {
    backgroundContainer: document.getElementById('background-container'),
    overlay: document.getElementById('overlay'),
    titleText: document.getElementById('title-text'),
    subtitleText: document.getElementById('subtitle-text'),
    nameText: document.getElementById('name-text'),
    usernameText: document.getElementById('username-text'),
    descriptionText: document.getElementById('description-text'),
    buttonsContainer: document.getElementById('buttons-container'),
    socialLinks: document.getElementById('social-links'),
    imageInfo: document.getElementById('image-info'),
    changeBgBtn: document.getElementById('change-bg-btn'),
    modal: document.getElementById('modal'),
    closeModalBtn: document.getElementById('close-modal'),
    modalTitle: document.getElementById('modal-title'),
    modalContent: document.getElementById('modal-content')
};

// 初始化应用
async function initApp() {
    try {
        const response = await fetch('config.json');
        config = await response.json();

        initStyles();
        initContent();
        initButtons();
        initSocialLinks();
        loadRandomBackground();
        addEventListeners();

        document.title = `${config.site.defaultTitle} | ${config.site.title}`;

    } catch (error) {
        console.error('初始化应用失败:', error);
        showError('无法加载配置，请检查网络连接或配置文件');
    }
}

// 初始化样式
function initStyles() {
    // 设置遮罩透明度
    elements.overlay.style.backgroundColor = `rgba(0, 0, 0, ${config.styles.overlayOpacity / 100})`;

    // 设置文本透明度
    const textElements = document.querySelectorAll('.text-opacity');
    textElements.forEach(el => {
        el.style.opacity = config.styles.textOpacity / 100;
    });
}

// 初始化内容
function initContent() {
    // 如果是首次加载，随机选择标题和副标题
    if (isFirstLoad && !localStorage.getItem('titleSelected')) {
        const randomTitle = getRandomItem(config.site.titleOptions);
        const randomSubtitle = getRandomItem(config.site.subtitleOptions);

        config.site.title = randomTitle;
        config.site.subtitle = randomSubtitle;

        localStorage.setItem('titleSelected', 'true');
        localStorage.setItem('siteTitle', randomTitle);
        localStorage.setItem('siteSubtitle', randomSubtitle);
    } else if (localStorage.getItem('siteTitle')) {
        // 使用本地存储的值
        config.site.title = localStorage.getItem('siteTitle');
        config.site.subtitle = localStorage.getItem('siteSubtitle');
    }

    // 更新DOM元素
    elements.titleText.textContent = config.site.title;
    elements.subtitleText.textContent = config.site.subtitle;
    elements.nameText.textContent = config.site.name;
    elements.usernameText.textContent = config.site.username;
    elements.descriptionText.textContent = config.site.description;

    isFirstLoad = false;
}

// 初始化按钮
function initButtons() {
    elements.buttonsContainer.innerHTML = '';

    config.buttons.forEach(button => {
        const buttonElement = createButton(button);
        elements.buttonsContainer.appendChild(buttonElement);
    });
}

// 创建按钮元素
function createButton(buttonConfig) {
    const button = document.createElement(buttonConfig.type === 'link' ? 'a' : 'button');

    // 添加基础类名
    button.className = `btn-hover-effect glass-card border-2 rounded-full px-8 py-3 text-lg font-medium text-white hover:bg-white hover:bg-opacity-10 hover:border-opacity-100 flex items-center`;

    // 设置边框透明度
    button.style.borderColor = `rgba(255, 255, 255, ${config.styles.buttonBorderOpacity / 100})`;

    // 设置按钮属性
    if (buttonConfig.type === 'link') {
        button.href = buttonConfig.url;
        if (buttonConfig.target) {
            button.target = buttonConfig.target;
        }
    } else {
        button.type = 'button';
        button.dataset.modalTitle = buttonConfig.modalTitle;
        button.dataset.modalContent = buttonConfig.modalContent;
        button.addEventListener('click', handleButtonClick);
    }

    // 设置按钮ID
    button.id = `${buttonConfig.id}-btn`;

    // 添加图标和文本
    button.innerHTML = `
        <i class="${buttonConfig.icon} mr-3 text-xl"></i>
        ${buttonConfig.text}
    `;

    return button;
}

// 初始化社交媒体链接
function initSocialLinks() {
    elements.socialLinks.innerHTML = '';

    config.socialLinks.forEach(link => {
        const linkElement = document.createElement('a');
        linkElement.href = link.url;
        linkElement.target = '_blank';
        linkElement.className = `opacity-80 hover:opacity-100 transition ${link.color}`;
        linkElement.innerHTML = `<i class="${link.icon}"></i>`;

        elements.socialLinks.appendChild(linkElement);
    });
}

// 处理按钮点击事件
function handleButtonClick(event) {
    const button = event.currentTarget;
    const title = button.dataset.modalTitle;
    const content = button.dataset.modalContent;

    showModal(title, content);
}

// 显示模态框
function showModal(title, content) {
    elements.modalTitle.textContent = title;
    elements.modalContent.innerHTML = content;
    elements.modal.classList.remove('hidden');
}

// 隐藏模态框
function hideModal() {
    elements.modal.classList.add('hidden');
}

// 加载随机背景图片
async function loadRandomBackground() {
    try {
        elements.imageInfo.textContent = '加载中...';
        elements.changeBgBtn.disabled = true;

        const response = await fetch(config.background.apiUrl);
        const data = await response.json();

        // 设置背景图片
        elements.backgroundContainer.style.backgroundImage = `url('${data.url}')`;

        // 显示图片信息
        elements.imageInfo.textContent = `尺寸: ${data.width} × ${data.height}`;

        // 添加淡入效果
        elements.backgroundContainer.style.opacity = 0;
        setTimeout(() => {
            elements.backgroundContainer.style.opacity = 1;
        }, 50);

        // 保存当前背景URL到本地存储
        localStorage.setItem('lastBackgroundUrl', data.url);

    } catch (error) {
        console.error('加载背景图片失败:', error);
        elements.imageInfo.textContent = '加载失败，使用默认背景';

        // 使用默认背景
        elements.backgroundContainer.style.backgroundImage = config.background.defaultBackground;

        // 检查是否有上次保存的背景
        const lastBackground = localStorage.getItem('lastBackgroundUrl');
        if (lastBackground) {
            elements.backgroundContainer.style.backgroundImage = `url('${lastBackground}')`;
            elements.imageInfo.textContent = '使用上次的缓存背景';
        }
    } finally {
        elements.changeBgBtn.disabled = false;
    }
}

// 添加事件监听器
function addEventListeners() {
    // 更换背景按钮
    elements.changeBgBtn.addEventListener('click', loadRandomBackground);

    // 关闭模态框按钮
    elements.closeModalBtn.addEventListener('click', hideModal);

    // 点击模态框外部关闭
    elements.modal.addEventListener('click', (e) => {
        if (e.target === elements.modal) {
            hideModal();
        }
    });

    // 标题和副标题点击编辑
    elements.titleText.addEventListener('click', () => {
        editText('标题', elements.titleText, (newText) => {
            config.site.title = newText;
            localStorage.setItem('siteTitle', newText);
            document.title = `${config.site.defaultTitle} | ${newText}`;
        });
    });

    elements.subtitleText.addEventListener('click', () => {
        editText('副标题', elements.subtitleText, (newText) => {
            config.site.subtitle = newText;
            localStorage.setItem('siteSubtitle', newText);
        });
    });

    // 描述点击编辑
    elements.descriptionText.addEventListener('click', () => {
        editText('描述', elements.descriptionText, (newText) => {
            config.site.description = newText;
            localStorage.setItem('siteDescription', newText);
        }, true);
    });
}

// 编辑文本
function editText(label, element, callback, isMultiline = false) {
    let currentText = element.textContent;

    if (isMultiline) {
        currentText = prompt(`${label} (多行文本):`, currentText);
    } else {
        currentText = prompt(`输入新的${label}:`, currentText);
    }

    if (currentText && currentText.trim()) {
        element.textContent = currentText.trim();
        callback(currentText.trim());
    }
}

// 显示错误信息
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg z-50';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// 获取随机项
function getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

// 初始化应用
document.addEventListener('DOMContentLoaded', initApp);