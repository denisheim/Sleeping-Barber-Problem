# This file defines the PyQt5-based user interface for the Sleeping Barber simulation.
# The UI displays the barber's status, the waiting customers, logs of events, and
# real-time statistics about served customers.
#
# The simulation is integrated with the UI through callbacks and signals.
# Users must press "Start" to begin the simulation.

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QListWidget, QTabWidget, QLabel, QAction, QToolBar,
                             QFrame, QTableWidget, QTableWidgetItem, QMenuBar, QMenu,
                             QStatusBar, QDialog, QDialogButtonBox, QPushButton,
                             QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject


class LogSignal(QObject):
    """
    A signal-emitting object used to forward log messages from background threads
    to the UI thread safely.
    """
    new_log = pyqtSignal(str)


class AboutDialog(QDialog):
    """
    A simple 'About' dialog providing information about the application.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Sleeping Barber Simulation")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout(self)

        info_label = QLabel("<h3>Sleeping Barber Simulation</h3>")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # OK button to close the dialog
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(self.accept)
        layout.addWidget(btns)


class MainWindow(QMainWindow):
    """
    The main window of the application.
    Displays:
    - Top panel with 'Start' and 'Quit' buttons.
    - Barber status and indicator.
    - Waiting room list.
    - Tabs for logs and statistics.
    - Status bar for simulation state messages.

    The simulation is passed in, and only starts after the 'Start' button is pressed.
    """

    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.setWindowTitle("Sleeping Barber Simulation")
        self.resize(1000, 700)

        # Tracks whether the simulation has started or not.
        # Initially False, user must press 'Start' to begin.
        self.simulation_started = False

        # Set up central widget and main layout.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top panel with Start and Quit buttons.
        # This makes it very clear how to start or end the simulation.
        top_frame = QFrame()
        top_frame.setFrameShape(QFrame.StyledPanel)
        top_frame.setFrameShadow(QFrame.Raised)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(20)

        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("font-size:18px; font-weight:bold; padding:10px;")
        self.start_button.clicked.connect(self.run_simulation)

        self.quit_button = QPushButton("Quit")
        self.quit_button.setStyleSheet("font-size:18px; font-weight:bold; padding:10px;")
        self.quit_button.clicked.connect(self.quit_app)

        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        top_layout.addWidget(self.quit_button)
        top_layout.addStretch()
        main_layout.addWidget(top_frame)

        # Barber Status Section
        # Shows if the barber is sleeping, cutting hair, or idle.
        self.barber_status_frame = QFrame()
        self.barber_status_frame.setFrameShape(QFrame.StyledPanel)
        self.barber_status_frame.setFrameShadow(QFrame.Raised)
        barber_layout = QHBoxLayout(self.barber_status_frame)
        barber_layout.setContentsMargins(10, 10, 10, 10)
        barber_layout.setSpacing(10)

        # Colored indicator representing barber's state.
        self.barber_indicator = QFrame()
        self.barber_indicator.setFixedSize(20, 20)
        self.barber_indicator.setStyleSheet("background-color: grey; border-radius: 10px;")

        self.barber_status_label = QLabel("Barber Status: Not Running")
        self.barber_status_label.setStyleSheet("font-size: 14px;")

        barber_layout.addWidget(self.barber_indicator)
        barber_layout.addWidget(self.barber_status_label, 1, Qt.AlignLeft)
        main_layout.addWidget(self.barber_status_frame)

        # Waiting Room Section
        # Shows all currently waiting customers.
        waiting_group = QGroupBox("Waiting Room")
        waiting_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; }")
        waiting_layout = QVBoxLayout(waiting_group)
        self.waiting_list = QListWidget()
        self.waiting_list.setStyleSheet("font-size: 13px;")
        waiting_layout.addWidget(self.waiting_list)
        main_layout.addWidget(waiting_group, 1)

        # Tabs: Logs and Statistics
        self.tabs = QTabWidget()

        # Logs Tab
        # Displays event logs from the simulation (barber events, customers arrival, etc.).
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(2)
        self.log_table.setHorizontalHeaderLabels(["Role", "Message"])
        self.log_table.horizontalHeader().setStretchLastSection(True)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setColumnWidth(0, 150)
        self.log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.log_table.setSelectionMode(QTableWidget.SingleSelection)

        self.logs_tab = QWidget()
        logs_layout = QVBoxLayout(self.logs_tab)
        logs_layout.setContentsMargins(5, 5, 5, 5)
        logs_layout.addWidget(self.log_table)
        self.tabs.addTab(self.logs_tab, "Logs")

        # Statistics Tab
        # Shows real computed stats: average wait, cut time, customers served, left, and waiting.
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        stats_layout.setContentsMargins(10, 10, 10, 10)

        stats_label = QLabel("<h3>Statistics (Real Data)</h3>")
        stats_label.setStyleSheet("font-size:16px; font-weight:bold;")
        stats_layout.addWidget(stats_label)

        # Labels for statistical values
        self.stat_served = QLabel("Customers Served: 0")
        self.stat_left = QLabel("Customers Left: 0")
        self.stat_wait = QLabel("Average Wait: N/A")
        self.stat_cut = QLabel("Average Cut: N/A")
        self.stat_waiting = QLabel("Currently Waiting: 0")

        stats_layout.addWidget(self.stat_served)
        stats_layout.addWidget(self.stat_left)
        stats_layout.addWidget(self.stat_wait)
        stats_layout.addWidget(self.stat_cut)
        stats_layout.addWidget(self.stat_waiting)

        # Additional info text to explain the statistics
        self.stats_info = QTextEdit()
        self.stats_info.setReadOnly(True)
        self.stats_info.setStyleSheet("font-size:12px;")
        self.stats_info.setPlainText(
            "Details:\n"
            "- This tab shows statistics from the simulation.\n"
            "- Average Wait Time: Average (start_cut_time - arrival_time).\n"
            "- Average Cut Time: Average (end_cut_time - start_cut_time).\n"
            "- Customers Left: How many left because the waiting room was full.\n"
            "- Currently Waiting: How many customers are waiting right now.\n"
            "- Values update as the simulation runs."
        )
        stats_layout.addWidget(self.stats_info, 1)

        self.tabs.addTab(self.stats_tab, "Statistics")

        main_layout.addWidget(self.tabs, 2)

        # Menubar
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Quit", self.quit_app)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        self.setMenuBar(menubar)

        # Status Bar
        # Displays messages like "Waiting for user to start the simulation..." or "Simulation Running..."
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Waiting for user to start the simulation...")

        # Log signals connect background logger events to UI updates
        self.log_signal = LogSignal()
        self.log_signal.new_log.connect(self.add_log_entry)

        self.simulation.logger.callback = self.log_callback

        # A timer updates the UI periodically (e.g. barber status, waiting room, stats)
        # Runs every 500ms.
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_ui)
        self.refresh_timer.start(500)

    def show_about_dialog(self):
        """
        Opens the about dialog providing information about the application.
        """
        dlg = AboutDialog(self)
        dlg.exec_()

    def run_simulation(self):
        """
        Called when the user presses 'Start'.
        Starts the simulation threads and the barber shop activity.
        Once started, the simulation will run until all customers are served or stopped.
        """
        if self.simulation_started:
            return
        self.simulation_started = True
        self.simulation.start_simulation()
        self.status_bar.showMessage("Simulation Running...")
        self.barber_status_label.setText("Barber Status: Sleeping")
        self.barber_indicator.setStyleSheet("background-color: blue; border-radius: 10px;")

    def log_callback(self, msg: str):
        """
        Callback from the logger. This is called in background threads.
        We use a signal to ensure thread-safe UI updates.
        """
        self.log_signal.new_log.emit(msg)

    def add_log_entry(self, msg: str):
        """
        Append a log message to the log table.
        Strips [INFO], [WARNING], [ERROR] tags from messages for cleaner display.
        """
        parts = msg.split(" ", 2)
        timestamp = ""
        message = msg
        if len(parts) > 2:
            timestamp = parts[0] + " " + parts[1]
            remainder = parts[2]
            remainder = remainder.replace("[INFO]", "").replace("[WARNING]", "").replace("[ERROR]", "").strip()
            message = remainder

        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        time_item = QTableWidgetItem(timestamp)
        message_item = QTableWidgetItem(message)

        # Make sure these cells are read-only.
        time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
        message_item.setFlags(message_item.flags() & ~Qt.ItemIsEditable)

        self.log_table.setItem(row, 0, time_item)
        self.log_table.setItem(row, 1, message_item)

        # Limit the log size to avoid huge tables.
        max_logs = 500
        if self.log_table.rowCount() > max_logs:
            self.log_table.removeRow(0)

        self.log_table.scrollToBottom()

    def update_ui(self):
        """
        Periodically updates the UI:
        - Barber status/indicator
        - Waiting room customers
        - Simulation statistics (if any customers have been served)
        - Status bar message

        If simulation ended, stops refreshing.
        """
        if not self.simulation_started:
            return

        barber = self.simulation.barber
        if self.simulation.is_done():
            self.status_bar.showMessage("Simulation Ended.")
        else:
            self.status_bar.showMessage("Simulation Running...")

        # Update barber state indicator
        if barber.is_sleeping:
            self.barber_status_label.setText("Barber Status: Sleeping")
            self.barber_indicator.setStyleSheet("background-color: blue; border-radius: 10px;")
        elif barber.current_customer is not None:
            self.barber_status_label.setText(f"Barber Status: Cutting hair for {barber.current_customer.name}")
            self.barber_indicator.setStyleSheet("background-color: green; border-radius: 10px;")
        else:
            self.barber_status_label.setText("Barber Status: Idle (awake)")
            self.barber_indicator.setStyleSheet("background-color: yellow; border-radius: 10px;")

        # Update waiting room list
        waiting_room = self.simulation.waiting_room
        self.waiting_list.clear()
        with waiting_room.lock:
            for cust in waiting_room.customers:
                self.waiting_list.addItem(cust.name)

        # Update statistics
        stats = self.simulation.compute_real_stats()
        served_count = stats["served_count"]
        left_count = stats["left_count"]
        waiting_count = stats["waiting_count"]

        self.stat_served.setText(f"Customers Served: {served_count}")
        self.stat_left.setText(f"Customers Left: {left_count}")
        self.stat_waiting.setText(f"Currently Waiting: {waiting_count}")

        if stats["avg_wait"] is not None:
            self.stat_wait.setText(f"Average Wait: {stats['avg_wait']:.2f} s")
        else:
            self.stat_wait.setText("Average Wait: N/A")

        if stats["avg_cut"] is not None:
            self.stat_cut.setText(f"Average Cut: {stats['avg_cut']:.2f} s")
        else:
            self.stat_cut.setText("Average Cut: N/A")

        # If simulation ended, stop updating the UI.
        if self.simulation.is_done():
            self.refresh_timer.stop()

    def quit_app(self):
        """
        Called when 'Quit' is pressed or from File->Quit menu.
        Stops the simulation and closes the application.
        """
        self.simulation.stop()
        self.close()


def run_app(simulation):
    """
    Creates and runs the QApplication main loop, showing the main window.
    """
    app = QApplication(sys.argv)
    window = MainWindow(simulation)
    window.show()
    sys.exit(app.exec_())
