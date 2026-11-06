"""Photoshop-style Font Picker Dialog with Family-Style tree, real-time preview & search."""
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QFileDialog, QRadioButton,
    QButtonGroup, QFrame, QSplitter
)
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import Qt, Signal
from app.core.font_manager import FontManager, FontVariant, FontFamily

class FontPickerDialog(QDialog):
    fontSelected = Signal(str, str) # family, font_path

    def __init__(self, current_font_path: str = "", sample_text: str = "Sample", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bộ Chọn Font Family — Chuẩn Photoshop (PSD)")
        self.resize(750, 580)
        self.setMinimumSize(600, 450)

        self.font_mgr = FontManager.get_instance()
        self.current_font_path = current_font_path or "C:/Windows/Fonts/arialbd.ttf"
        self.sample_text = sample_text or "Sample"
        self.selected_variant: FontVariant = None

        self._init_ui()
        self._populate_tree()
        self._highlight_current_font()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 1. Top bar: Search input & Sample text preview changer
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        lbl_search = QLabel("🔍")
        lbl_search.setStyleSheet("font-size: 16px;")
        search_row.addWidget(lbl_search)

        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("Tìm kiếm font family hoặc style (ví dụ: Zurich, Impact, Bold, VNI)...")
        self.edit_search.setClearButtonEnabled(True)
        self.edit_search.textChanged.connect(self._filter_tree)
        search_row.addWidget(self.edit_search, 1)

        lbl_sample = QLabel("Mẫu chữ:")
        search_row.addWidget(lbl_sample)

        self.edit_sample = QLineEdit(self.sample_text)
        self.edit_sample.setFixedWidth(130)
        self.edit_sample.textChanged.connect(self._on_sample_text_changed)
        search_row.addWidget(self.edit_sample)

        main_layout.addLayout(search_row)

        # 2. Filter tabs (All / Favorites / Recent)
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.btn_group = QButtonGroup(self)
        self.rb_all = QRadioButton("Tất cả Fonts (All)")
        self.rb_fav = QRadioButton("⭐ Yêu thích (Favorites)")
        self.rb_recent = QRadioButton("🕒 Gần đây (Recent)")
        self.rb_all.setChecked(True)

        self.btn_group.addButton(self.rb_all)
        self.btn_group.addButton(self.rb_fav)
        self.btn_group.addButton(self.rb_recent)

        self.rb_all.toggled.connect(self._filter_tree)
        self.rb_fav.toggled.connect(self._filter_tree)
        self.rb_recent.toggled.connect(self._filter_tree)

        filter_row.addWidget(self.rb_all)
        filter_row.addWidget(self.rb_fav)
        filter_row.addWidget(self.rb_recent)
        filter_row.addStretch()

        btn_browse = QPushButton("📁 Mở file Font ngoài...")
        btn_browse.clicked.connect(self._browse_custom_font)
        filter_row.addWidget(btn_browse)

        main_layout.addLayout(filter_row)

        # 3. Central Tree Widget (Family / Style -> Preview)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Font Family & Biến thể Style", "Mẫu chữ trực quan (Preview)", "⭐"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tree.setColumnWidth(0, 310)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.itemSelectionChanged.connect(self._on_item_selected)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        main_layout.addWidget(self.tree, 1)

        # 4. Footer selection info and Actions
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.StyledPanel)
        footer_frame.setStyleSheet("background-color: #F8F9FA; border-radius: 4px; padding: 4px;")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(8, 6, 8, 6)

        v_info = QVBoxLayout()
        v_info.setSpacing(2)
        self.lbl_selected_title = QLabel("Font đang chọn: Chưa chọn")
        self.lbl_selected_title.setStyleSheet("font-weight: bold; color: #1961B5;")
        self.lbl_selected_path = QLabel("")
        self.lbl_selected_path.setStyleSheet("color: #666; font-size: 11px;")
        v_info.addWidget(self.lbl_selected_title)
        v_info.addWidget(self.lbl_selected_path)
        footer_layout.addLayout(v_info, 1)

        self.btn_fav_toggle = QPushButton("⭐ Thêm yêu thích")
        self.btn_fav_toggle.setEnabled(False)
        self.btn_fav_toggle.clicked.connect(self._toggle_favorite_selected)
        footer_layout.addWidget(self.btn_fav_toggle)

        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        footer_layout.addWidget(btn_cancel)

        self.btn_apply = QPushButton("✅ Chọn Font này")
        self.btn_apply.setEnabled(False)
        self.btn_apply.setStyleSheet("font-weight: bold; background-color: #1961B5; color: white; padding: 6px 14px; border-radius: 4px;")
        self.btn_apply.clicked.connect(self._accept_selection)
        footer_layout.addWidget(self.btn_apply)

        main_layout.addWidget(footer_frame)

    def _create_font(self, family: str, style: str) -> QFont:
        qf = QFont(family, 13)
        style_lower = style.lower()
        if any(w in style_lower for w in ("bold", "black", "heavy")):
            qf.setBold(True)
        if "italic" in style_lower or "oblique" in style_lower:
            qf.setItalic(True)
        return qf

    def _populate_tree(self):
        self.tree.clear()
        families = self.font_mgr.get_sorted_families()

        for fam in families:
            is_fav = self.font_mgr.is_favorite(fam.name)
            star = "⭐" if is_fav else ""

            if len(fam.variants) == 1:
                # Single variant family
                v = fam.variants[0]
                item = QTreeWidgetItem([f"{fam.name} ({v.style})", self.sample_text, star])
                item.setFont(1, self._create_font(fam.name, v.style))
                item.setData(0, Qt.UserRole, v)
                item.setData(0, Qt.UserRole + 1, fam.name)
                self.tree.addTopLevelItem(item)
            else:
                # Multi-variant family (Tree grouping)
                parent_item = QTreeWidgetItem([f"{fam.name}  [{len(fam.variants)} styles]", "", star])
                parent_item.setFont(0, QFont(fam.name, 10, QFont.Bold))
                parent_item.setData(0, Qt.UserRole + 1, fam.name)
                default_v = fam.get_default_variant()
                parent_item.setData(0, Qt.UserRole, default_v)

                for v in fam.variants:
                    child_item = QTreeWidgetItem([f"  ↳ {v.style}", self.sample_text, ""])
                    child_item.setFont(1, self._create_font(fam.name, v.style))
                    child_item.setData(0, Qt.UserRole, v)
                    child_item.setData(0, Qt.UserRole + 1, fam.name)
                    parent_item.addChild(child_item)

                self.tree.addTopLevelItem(parent_item)

    def _highlight_current_font(self):
        """Scrolls to and selects the current font variant."""
        target_path = os.path.normpath(self.current_font_path).lower()
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            v = top.data(0, Qt.UserRole)
            if v and os.path.normpath(v.path).lower() == target_path:
                self.tree.setCurrentItem(top)
                self.tree.scrollToItem(top)
                return
            for j in range(top.childCount()):
                child = top.child(j)
                cv = child.data(0, Qt.UserRole)
                if cv and os.path.normpath(cv.path).lower() == target_path:
                    top.setExpanded(True)
                    self.tree.setCurrentItem(child)
                    self.tree.scrollToItem(child)
                    return

    def _filter_tree(self):
        query = self.edit_search.text().strip().lower()
        filter_fav = self.rb_fav.isChecked()
        filter_recent = self.rb_recent.isChecked()

        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            fam_name = top.data(0, Qt.UserRole + 1) or ""
            is_fav = self.font_mgr.is_favorite(fam_name)

            if filter_fav and not is_fav:
                top.setHidden(True)
                continue

            # Check children
            child_matches = 0
            for j in range(top.childCount()):
                child = top.child(j)
                cv: FontVariant = child.data(0, Qt.UserRole)
                if not cv:
                    continue

                if filter_recent and os.path.normpath(cv.path) not in self.font_mgr.recent_paths:
                    child.setHidden(True)
                    continue

                text_matched = (not query) or (query in fam_name.lower()) or (query in cv.style.lower()) or (query in cv.full_name.lower())
                child.setHidden(not text_matched)
                if text_matched:
                    child_matches += 1

            if top.childCount() > 0:
                top_matches = (not query) or (query in fam_name.lower())
                top.setHidden((child_matches == 0) and (not top_matches))
                if query and child_matches > 0:
                    top.setExpanded(True)
            else:
                v: FontVariant = top.data(0, Qt.UserRole)
                if not v:
                    top.setHidden(True)
                    continue
                if filter_recent and os.path.normpath(v.path) not in self.font_mgr.recent_paths:
                    top.setHidden(True)
                    continue
                text_matched = (not query) or (query in fam_name.lower()) or (query in v.style.lower())
                top.setHidden(not text_matched)

    def _on_sample_text_changed(self, text: str):
        self.sample_text = text or "Sample"
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            if top.childCount() == 0:
                top.setText(1, self.sample_text)
            for j in range(top.childCount()):
                top.child(j).setText(1, self.sample_text)

    def _on_item_selected(self):
        item = self.tree.currentItem()
        if not item:
            self.btn_apply.setEnabled(False)
            self.btn_fav_toggle.setEnabled(False)
            return

        variant: FontVariant = item.data(0, Qt.UserRole)
        fam_name = item.data(0, Qt.UserRole + 1) or ""

        if variant:
            self.selected_variant = variant
            self.lbl_selected_title.setText(f"Font: {variant.family} — {variant.style}")
            self.lbl_selected_path.setText(f"Đường dẫn: {variant.path}")
            self.btn_apply.setEnabled(True)
        else:
            self.selected_variant = None
            self.lbl_selected_title.setText(f"Họ font: {fam_name}")
            self.lbl_selected_path.setText("")
            self.btn_apply.setEnabled(False)

        is_fav = self.font_mgr.is_favorite(fam_name)
        self.btn_fav_toggle.setText("⭐ Bỏ yêu thích" if is_fav else "⭐ Thêm yêu thích")
        self.btn_fav_toggle.setEnabled(bool(fam_name))

    def _on_item_double_clicked(self, item, column):
        variant: FontVariant = item.data(0, Qt.UserRole)
        if variant:
            self.selected_variant = variant
            self._accept_selection()

    def _toggle_favorite_selected(self):
        item = self.tree.currentItem()
        if not item:
            return
        fam_name = item.data(0, Qt.UserRole + 1)
        if fam_name:
            self.font_mgr.toggle_favorite(fam_name)
            is_fav = self.font_mgr.is_favorite(fam_name)
            self.btn_fav_toggle.setText("⭐ Bỏ yêu thích" if is_fav else "⭐ Thêm yêu thích")
            # Update star column
            top_item = item if item.parent() is None else item.parent()
            top_item.setText(2, "⭐" if is_fav else "")

    def _browse_custom_font(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Font ngoài", "C:/Windows/Fonts", "Fonts (*.ttf *.otf)"
        )
        if path:
            v = self.font_mgr.add_custom_font(path)
            if v:
                self._populate_tree()
                self.current_font_path = path
                self._highlight_current_font()
                self._on_item_selected()

    def _accept_selection(self):
        if self.selected_variant:
            self.font_mgr.add_recent(self.selected_variant.path)
            self.fontSelected.emit(self.selected_variant.family, self.selected_variant.path)
            self.accept()

    def get_selected_font(self) -> Tuple[str, str]:
        """Returns (family_name, font_file_path)."""
        if self.selected_variant:
            return self.selected_variant.family, self.selected_variant.path
        return "Arial", "C:/Windows/Fonts/arialbd.ttf"
