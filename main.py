1import sys
import json
from PyQt5.QtCore import Qt, QUrl, QEvent
from PyQt5.QtGui import QIcon
import yaml
import os
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QTabBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
if os.path.exists("option.yml"):
    print("fore")
else:
    with open("option.yml","w") as f:
        f.write('version: 4.6\nadblock: "true"\nname: "Navigateur Intenet"\n#seul les .ico fonctionne ,lien absolue \nicon: "default"')


# Chemin vers le fichier YAML
fichier_yaml = "option.yml"

# Lecture du fichier YAML
with open(fichier_yaml, 'r') as file:
    contenu = yaml.safe_load(file)

# Accéder aux valeurs dans le fichier YAML
if 'version' in contenu:
    valeur_test = contenu['version']
if 'name' in contenu:
    valeur_name = contenu['name']
if 'icon' in contenu:
    valeur_icon = contenu['icon']

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, ad_keywords):
        super().__init__()
        self.ad_keywords = ad_keywords

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        for keyword in self.ad_keywords:
            if keyword in url:
                info.block(True)
                return

class Browser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{valeur_name} V.{valeur_test}')
        if(valeur_icon == "default"):
            self.setWindowIcon(QIcon('icon.ico'))
        else:
            self.setWindowIcon(QIcon(valeur_icon))
        self.setGeometry(0, 0, 1000, 900)
        self.setStyleSheet("background-color: #40E0D0;")

        # Initialize ad blocker and ad keywords
        self.ad_keywords = ["doubleclick.net", "googleadservices.com", "examplead.com"]
        self.ad_blocker = AdBlocker(self.ad_keywords)

        self.UiComponents()
        self.show()

    def UiComponents(self):
        layout = QVBoxLayout(self)

        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        self.url_entry = QLineEdit(self)
        grid_layout.addWidget(self.url_entry, 0, 4, 1, 5)
        self.url_entry.returnPressed.connect(self.load_url)

        


        reload_btn = QPushButton('🗘', self)
        grid_layout.addWidget(reload_btn, 0 , 2)
        

        back_button = QPushButton("←", self)
        grid_layout.addWidget(back_button, 0, 0)

        forward_button = QPushButton("→", self)
        grid_layout.addWidget(forward_button, 0, 3)

        go_button = QPushButton("⚙", self)
        grid_layout.addWidget(go_button, 0, 11)
        go_button.clicked.connect(self.create_new_tab_with_switch)

        new_tab_button = QPushButton("+", self)
        grid_layout.addWidget(new_tab_button, 0, 10)
        
    # ...
        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)
        self.tab_widget.currentChanged.connect(self.update_url_entry)

        reload_btn.clicked.connect(self.reload_page)
        go_button.clicked.connect(self.load_url)
        back_button.clicked.connect(self.go_back)
        new_tab_button.clicked.connect(self.create_new_tab)
        forward_button.clicked.connect(self.go_forward)

        self.create_new_tab()

    def create_new_tab(self):
        web_view = QWebEngineView(self)
        self.tab_widget.addTab(web_view, "Nouvel Onglet")
        self.tab_widget.setCurrentWidget(web_view)
        web_view.titleChanged.connect(self.update_tab_title)
        web_view.urlChanged.connect(self.update_url_entry)
        web_view.setStyleSheet("background-color: #40E0D0;")

        # Add close button to tab bar
        close_button = QPushButton("⨯")
        close_button.clicked.connect(self.close_tab)
        index = self.tab_widget.indexOf(web_view)
        self.tab_widget.tabBar().setTabButton(index, QTabBar.RightSide, close_button)
        close_button.setStyleSheet("background-color: #FF0000;")
        web_view.installEventFilter(self)

       

        # Add content blocker for ad elements
        self.inject_content_blocker(web_view)

    def inject_content_blocker(self, web_view):
        content_blocker_script = """
        const ad_keywords = {keywords};
        function blockAds() {{
            const elements = document.querySelectorAll('div, span, img');
            elements.forEach(element => {{
                const src = element.tagName === 'IMG' ? element.src : element.getAttribute('src');
                if (src && ad_keywords.some(keyword => src.includes(keyword))) {{
                    element.style.display = 'none';
                }}
            }});
        }}
        document.addEventListener('DOMContentLoaded', blockAds);
        """
        content_blocker_script = content_blocker_script.replace('{keywords}', json.dumps(self.ad_keywords))

        web_view.page().runJavaScript(content_blocker_script)

    def load_url(self):
        url = "https://" + self.url_entry.text()
        current_web_view = self.tab_widget.currentWidget()
    
        def handle_load_finished(ok):
            if not ok:
                
                url_for_error = self.url_entry.text().replace(" ", "+")
                url_for_error = self.url_entry.text().replace("https://", "")
                current_web_view.load(QUrl(f"https://search.brave.com/search?q={url_for_error}&source=web"))
        current_web_view.load(QUrl(url))
        current_web_view.page().loadFinished.connect(handle_load_finished)
    
        
        





    def update_tab_title(self, title):
        current_web_view = self.tab_widget.currentWidget()
        index = self.tab_widget.indexOf(current_web_view)
        self.tab_widget.setTabText(index, title)

    def update_url_entry(self, index):
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            url = current_web_view.url().toString()
            self.url_entry.setText(url)

    def go_back(self):
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.back()

    def go_forward(self):
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.forward()

    def reload_page(self):
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.reload()

    def close_tab(self):
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.deleteLater()
            index = self.tab_widget.currentIndex()
            self.tab_widget.removeTab(index)
            self.web_page_profiles.pop(index)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        if event.key() == Qt.Key_F5:
            self.reload_page()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    def create_new_tab_with_switch(self):
        new_web_view = QWebEngineView(self)
        self.tab_widget.addTab(new_web_view, "New Tab")
        self.tab_widget.setCurrentWidget(new_web_view)
    
        # Load a page with a "switch" content
        switch_page_content = """
            <html>
            <head>
                <title>Settings</title>
            </head>
            <body>
                <h1>Settings</h1>
                
                loading.. fail to open  option.yml result: ❌ please using Sublime Text 3/visual studio code for edit option.yml 
            </body>
            </html>
            <style type="text/css">h1{text-align: center;} </style>
        """
        new_web_view.setHtml(switch_page_content)
    
        new_web_view.page().loadFinished.connect(self.handle_load_finished_new_tab)
    def handle_load_finished_new_tab(self, ok):
        if not ok:
            current_web_view = self.tab_widget.currentWidget()
            print("Error loading:", current_web_view.url().toString())

            # Display an error message in the current tab
            error_message = f"Unable to access the website: {current_web_view.url().toString()}"
            current_web_view.setHtml(error_message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Browser()
    sys.exit(app.exec_())
