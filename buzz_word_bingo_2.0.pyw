# buzz_word_bingo.py
import tkinter as tk
import random
from datetime import datetime
import math


class Confetti:
    """Manages confetti particle animations."""
    
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.particles = []
        self.active = False
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                       '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52C77A']
        self.spawn_confetti(x, y)
    
    def spawn_confetti(self, center_x, center_y):
        """Create confetti particles."""
        for _ in range(40):  # Reduced for smaller area
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)  # Reduced speed for smaller area
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(1, 3)  # Less vertical speed
            
            size = random.randint(4, 8)  # Smaller particles
            color = random.choice(self.colors)
            shape = random.choice(['oval', 'rectangle'])
            
            if shape == 'oval':
                particle = self.canvas.create_oval(
                    center_x, center_y,
                    center_x + size, center_y + size,
                    fill=color, outline=color
                )
            else:
                particle = self.canvas.create_rectangle(
                    center_x, center_y,
                    center_x + size, center_y + size,
                    fill=color, outline=color
                )
            
            self.particles.append({
                'id': particle,
                'x': center_x,
                'y': center_y,
                'vx': vx,
                'vy': vy,
                'gravity': 0.2,  # Reduced gravity
                'life': 80  # Shorter lifetime
            })
        
        self.active = True
        self.animate()
    
    def animate(self):
        """Animate confetti particles."""
        if not self.active:
            return
        
        active_particles = []
        for particle in self.particles:
            particle['vy'] += particle['gravity']
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # Keep particles within 100px height bounds
            if particle['life'] > 0 and particle['y'] < 120:
                self.canvas.coords(
                    particle['id'],
                    particle['x'], particle['y'],
                    particle['x'] + 6, particle['y'] + 6
                )
                active_particles.append(particle)
            else:
                self.canvas.delete(particle['id'])
        
        self.particles = active_particles
        
        if self.particles:
            self.canvas.after(20, self.animate)
        else:
            self.active = False


class BingoBoard:
    """Manages the bingo board logic and state."""
    
    def __init__(self, buzzwords):
        self.buzzwords = buzzwords
        self.size = 5
        self.board = []
        self.marked = []
        self.free_space_pos = (2, 2)  # Center position (row 2, col 2)
        self.generate_board()
    
    def generate_board(self):
        """Generate a new randomized 5x5 board."""
        # Select 24 random buzzwords (25 - 1 for FREE SPACE)
        selected = random.sample(self.buzzwords, 24)
        
        # Build the board
        self.board = []
        idx = 0
        for row in range(self.size):
            board_row = []
            for col in range(self.size):
                if (row, col) == self.free_space_pos:
                    board_row.append("FREE SPACE")
                else:
                    board_row.append(selected[idx])
                    idx += 1
            self.board.append(board_row)
        
        # Initialize marked state
        self.marked = [[False] * self.size for _ in range(self.size)]
        self.marked[self.free_space_pos[0]][self.free_space_pos[1]] = True
    
    def toggle_mark(self, row, col):
        """Toggle the marked state of a tile (except FREE SPACE)."""
        if (row, col) != self.free_space_pos:
            self.marked[row][col] = not self.marked[row][col]
    
    def reset_marks(self):
        """Reset all marks except FREE SPACE."""
        self.marked = [[False] * self.size for _ in range(self.size)]
        self.marked[self.free_space_pos[0]][self.free_space_pos[1]] = True
    
    def check_bingo(self):
        """Check for bingo. Returns list of winning lines as (type, index) tuples."""
        winning_lines = []
        
        # Check rows
        for row in range(self.size):
            if all(self.marked[row][col] for col in range(self.size)):
                winning_lines.append(('row', row))
        
        # Check columns
        for col in range(self.size):
            if all(self.marked[row][col] for row in range(self.size)):
                winning_lines.append(('col', col))
        
        # Check diagonal (top-left to bottom-right)
        if all(self.marked[i][i] for i in range(self.size)):
            winning_lines.append(('diag', 0))
        
        # Check diagonal (top-right to bottom-left)
        if all(self.marked[i][self.size - 1 - i] for i in range(self.size)):
            winning_lines.append(('diag', 1))
        
        return winning_lines
    
    def get_board_text(self):
        """Return board as plain text (5 rows of 5)."""
        lines = []
        for row in self.board:
            lines.append('\t'.join(row))
        return '\n'.join(lines)


class RoundedButton(tk.Canvas):
    """Custom rounded button widget."""
    
    def __init__(self, parent, text, command, **kwargs):
        # Extract custom parameters
        bg_color = kwargs.pop('bg_color', '#6C5CE7')
        hover_color = kwargs.pop('hover_color', '#5F4DD1')
        text_color = kwargs.pop('text_color', 'white')
        width = kwargs.pop('width', 120)
        height = kwargs.pop('height', 40)
        
        tk.Canvas.__init__(self, parent, width=width, height=height, 
                          highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
        # Draw rounded rectangle
        self.rect = self.create_rounded_rect(2, 2, width-2, height-2, 
                                             radius=20, fill=bg_color, outline='')
        self.text = self.create_text(width/2, height/2, text=text, 
                                     fill=text_color, font=('Arial', 10, 'bold'))
        
        # Bind events
        self.tag_bind(self.rect, '<Button-1>', self._on_click)
        self.tag_bind(self.text, '<Button-1>', self._on_click)
        self.tag_bind(self.rect, '<Enter>', self._on_enter)
        self.tag_bind(self.text, '<Enter>', self._on_enter)
        self.tag_bind(self.rect, '<Leave>', self._on_leave)
        self.tag_bind(self.text, '<Leave>', self._on_leave)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_click(self, event):
        """Handle click event."""
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.itemconfig(self.rect, fill=self.hover_color)
        self.is_hovered = True
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        self.itemconfig(self.rect, fill=self.bg_color)
        self.is_hovered = False


class BingoTile(tk.Canvas):
    """Custom bingo tile widget with rounded corners."""
    
    def __init__(self, parent, text, command, row, col, **kwargs):
        width = kwargs.pop('width', 100)
        height = kwargs.pop('height', 100)
        
        tk.Canvas.__init__(self, parent, width=width, height=height,
                          highlightthickness=0, bg='#F0F3F7')
        
        self.command = command
        self.row = row
        self.col = col
        self.text_content = text
        self.is_marked = False
        self.is_winning = False
        self.is_free_space = (text == "FREE SPACE")
        
        # Colors
        self.normal_color = '#FFFFFF'
        self.marked_color = '#A8E6CF'
        self.winning_color = '#FFD93D'
        self.free_space_color = '#DDA0DD'
        self.border_color = '#E0E6ED'
        
        # Draw tile
        self.rect = self.create_rounded_rect(5, 5, width-5, height-5,
                                             radius=15, fill=self.normal_color,
                                             outline=self.border_color, width=2)
        
        # Add checkmark (hidden initially)
        self.check = self.create_text(width-15, 15, text='✓', 
                                      fill='#2ECC71', font=('Arial', 20, 'bold'),
                                      state='hidden')
        
        # Add text
        self.text = self.create_text(width/2, height/2, text=text,
                                     fill='#2C3E50', font=('Arial', 9, 'bold'),
                                     width=width-20)
        
        # Bind events
        self.tag_bind(self.rect, '<Button-1>', self._on_click)
        self.tag_bind(self.text, '<Button-1>', self._on_click)
        
        # Mark FREE SPACE initially
        if self.is_free_space:
            self.set_marked(True)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle."""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_click(self, event):
        """Handle click event."""
        if self.command:
            self.command(self.row, self.col)
    
    def set_marked(self, marked):
        """Set the marked state."""
        self.is_marked = marked
        self.update_appearance()
    
    def set_winning(self, winning):
        """Set the winning state."""
        self.is_winning = winning
        self.update_appearance()
    
    def update_appearance(self):
        """Update tile appearance based on state."""
        if self.is_winning:
            color = self.winning_color
            self.itemconfig(self.check, state='normal')
        elif self.is_free_space:
            color = self.free_space_color
            self.itemconfig(self.check, state='normal')
        elif self.is_marked:
            color = self.marked_color
            self.itemconfig(self.check, state='normal')
        else:
            color = self.normal_color
            self.itemconfig(self.check, state='hidden')
        
        self.itemconfig(self.rect, fill=color)


class BingoUI:
    """Main UI for the Buzz-Word Bingo game."""
    
    def __init__(self, root, buzzwords):
        self.root = root
        self.root.title("Buzz-Word Bingo")
        self.root.configure(bg='#F0F3F7')
        self.board = BingoBoard(buzzwords)
        self.tile_widgets = []
        self.bingo_active = False
        self.winning_lines = []
        self.confetti = None
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main container with gradient effect
        main_frame = tk.Frame(self.root, bg='#F0F3F7')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with gradient background effect
        title_frame = tk.Frame(main_frame, bg='#6C5CE7', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 Buzz-Word Bingo 🎯",
            font=("Arial", 28, "bold"),
            fg='white',
            bg='#6C5CE7',
            pady=20
        )
        title_label.pack()
        
        # Status line with modern styling
        self.status_label = tk.Label(
            main_frame,
            text="Click tiles as you hear them. Free space is marked.",
            font=("Arial", 11),
            fg='#5F6368',
            bg='#F0F3F7',
            pady=10
        )
        self.status_label.pack()
        
        # Dedicated bingo banner area (always present, 100px height)
        self.bingo_area = tk.Frame(main_frame, bg='#F0F3F7', height=100)
        self.bingo_area.pack(fill=tk.X)
        self.bingo_area.pack_propagate(False)
        
        # Bingo banner (initially hidden) - will be placed in bingo_area
        self.bingo_banner = tk.Label(
            self.bingo_area,
            text="🎉 BINGO! 🎉",
            font=("Arial", 32, "bold"),
            fg='white',
            bg='#FF6B6B'
        )
        
        # Canvas for confetti animation (confined to bingo area)
        self.confetti_canvas = tk.Canvas(
            self.bingo_area,
            bg='#F0F3F7',
            highlightthickness=0,
            height=100
        )
        
        # Game board frame with reduced padding
        board_container = tk.Frame(main_frame, bg='#F0F3F7', padx=15, pady=10)
        board_container.pack(expand=True, fill=tk.BOTH)
        
        self.board_frame = tk.Frame(board_container, bg='#F0F3F7')
        self.board_frame.pack(expand=True)
        
        # Create 5x5 grid of custom tile widgets
        self.tile_widgets = []
        for row in range(5):
            tile_row = []
            for col in range(5):
                tile = BingoTile(
                    self.board_frame,
                    text=self.board.board[row][col],
                    command=self.on_tile_click,
                    row=row,
                    col=col,
                    width=100,
                    height=100
                )
                tile.grid(row=row, column=col, padx=3, pady=3)
                tile_row.append(tile)
            self.tile_widgets.append(tile_row)
        
        # Control buttons frame
        controls_frame = tk.Frame(main_frame, bg='#F0F3F7', pady=15)
        controls_frame.pack()
        
        button_configs = [
            ("New Board", self.new_board, '#6C5CE7', '#5F4DD1'),
            ("Reset Marks", self.reset_marks, '#00B894', '#00A182'),
        ]
        
        for text, command, bg, hover in button_configs:
            btn = RoundedButton(
                controls_frame,
                text=text,
                command=command,
                bg_color=bg,
                hover_color=hover,
                width=140,
                height=40,
                bg='#F0F3F7'
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Continue playing button (greyed out until bingo)
        self.continue_button = RoundedButton(
            controls_frame,
            text="Continue Playing",
            command=self.dismiss_bingo,
            bg_color='#95A5A6',
            hover_color='#95A5A6',
            width=160,
            height=40,
            bg='#F0F3F7'
        )
        self.continue_button.pack(side=tk.LEFT, padx=5)
        self.continue_button_enabled = False
        self.update_continue_button()
    
    def update_continue_button(self):
        """Update the continue button appearance based on bingo state."""
        if self.continue_button_enabled:
            # Enable button - green color
            self.continue_button.bg_color = '#2ECC71'
            self.continue_button.hover_color = '#27AE60'
            self.continue_button.itemconfig(self.continue_button.rect, fill='#2ECC71')
        else:
            # Disable button - grey color
            self.continue_button.bg_color = '#95A5A6'
            self.continue_button.hover_color = '#95A5A6'
            self.continue_button.itemconfig(self.continue_button.rect, fill='#95A5A6')
    
    def on_tile_click(self, row, col):
        """Handle tile click event."""
        self.board.toggle_mark(row, col)
        self.update_display()
        self.check_and_show_bingo()
    
    def update_display(self):
        """Update the visual state of all tiles."""
        for row in range(5):
            for col in range(5):
                tile = self.tile_widgets[row][col]
                is_marked = self.board.marked[row][col]
                is_winning = self.is_winning_tile(row, col)
                
                tile.set_marked(is_marked)
                tile.set_winning(is_winning and self.bingo_active)
    
    def is_winning_tile(self, row, col):
        """Check if a tile is part of a winning line."""
        if not self.winning_lines:
            return False
        
        for line_type, index in self.winning_lines:
            if line_type == 'row' and row == index:
                return True
            elif line_type == 'col' and col == index:
                return True
            elif line_type == 'diag' and index == 0 and row == col:
                return True
            elif line_type == 'diag' and index == 1 and row == (4 - col):
                return True
        
        return False
    
    def check_and_show_bingo(self):
        """Check for bingo and display banner if found."""
        self.winning_lines = self.board.check_bingo()
        
        if self.winning_lines and not self.bingo_active:
            self.bingo_active = True
            # Launch confetti first
            self.launch_confetti()
            # Show banner in the bingo area
            self.bingo_banner.place(relx=0.5, rely=0.5, anchor='center')
            # Ensure banner is on top of confetti canvas
            self.bingo_banner.lift()
            # Enable continue button
            self.continue_button_enabled = True
            self.update_continue_button()
            self.play_celebration_sound()
            self.update_display()
        elif not self.winning_lines and self.bingo_active:
            # If winning state removed (shouldn't happen but just in case)
            self.dismiss_bingo()
    
    def dismiss_bingo(self):
        """Dismiss the bingo celebration but keep winning tiles highlighted."""
        if not self.continue_button_enabled:
            return  # Button is disabled, don't do anything
        
        self.bingo_banner.place_forget()
        self.confetti_canvas.place_forget()
        # Disable continue button again
        self.continue_button_enabled = False
        self.update_continue_button()
        # Note: we keep self.bingo_active True and self.winning_lines intact
        # so the winning tiles remain highlighted
    
    def play_celebration_sound(self):
        """Play a celebratory sound sequence."""
        try:
            import winsound
            # Play a happy ascending tone sequence
            frequencies = [523, 659, 784, 1047]  # C, E, G, C (octave higher)
            for freq in frequencies:
                winsound.Beep(freq, 150)
        except:
            # Fallback to system bell on non-Windows or if winsound fails
            for _ in range(3):
                self.root.bell()
    
    def launch_confetti(self):
        """Launch confetti animation within the bingo area."""
        # Place canvas to fill the entire bingo area
        self.confetti_canvas.place(x=0, y=0, relwidth=1.0, height=100)
        self.confetti_canvas.delete('all')
        
        # Get canvas dimensions
        self.root.update_idletasks()
        canvas_width = self.confetti_canvas.winfo_width()
        
        # Create confetti at multiple positions across the width
        for _ in range(3):
            x = random.randint(100, max(200, canvas_width - 100))
            y = 50  # Middle of the 100px area
            Confetti(self.confetti_canvas, x, y)
    
    def new_board(self):
        """Generate a new randomized board."""
        # Remove old tiles
        for row in self.tile_widgets:
            for tile in row:
                tile.destroy()
        
        # Generate new board
        self.board.generate_board()
        self.bingo_active = False
        self.winning_lines = []
        self.bingo_banner.place_forget()
        self.confetti_canvas.place_forget()
        self.continue_button_enabled = False
        self.update_continue_button()
        
        # Create new tiles
        self.tile_widgets = []
        for row in range(5):
            tile_row = []
            for col in range(5):
                tile = BingoTile(
                    self.board_frame,
                    text=self.board.board[row][col],
                    command=self.on_tile_click,
                    row=row,
                    col=col,
                    width=100,
                    height=100
                )
                tile.grid(row=row, column=col, padx=3, pady=3)
                tile_row.append(tile)
            self.tile_widgets.append(tile_row)
        
        self.update_display()
    
    def reset_marks(self):
        """Reset all marks except FREE SPACE."""
        self.board.reset_marks()
        self.bingo_active = False
        self.winning_lines = []
        self.bingo_banner.place_forget()
        self.confetti_canvas.place_forget()
        self.continue_button_enabled = False
        self.update_continue_button()
        self.update_display()


def main():
    """Main entry point for the application."""
    buzzwords = [
        "Circle Back",
        "Low Hanging Fruit",
        "Take This Offline",
        "Deep Dive",
        "Synergy",
        "Bandwidth",
        "Action Items",
        "Touch Base",
        "Moving Forward",
        "Thought Leadership",
        "Quick Win",
        "Single Pane of Glass",
        "Customer Centric",
        "Best Practices",
        "Game Changer",
        "At Scale",
        "Leverage",
        "Alignment",
        "Deliverables",
        "Boil the Ocean",
        "Run It Up the Flagpole",
        "North Star",
        "Value Add",
        "Paradigm Shift",
        "Stakeholder Buy In",
        "Roadmap",
        "Pain Points",
        "Level Set",
        "Granular",
        "Drill Down",
        "Pivot",
        "Blockers",
        "Operationalize",
        "Right Size",
        "Optimize",
        "End of Day",
        "Low Effort High Impact",
        "Move the Needle",
        "Outside the Box",
        "Parking Lot",
        "Table This",
        "Socialize This",
        "Takeaway",
        "Key Learnings",
        "Win Win",
        "Close the Loop",
        "Circle the Wagons",
        "High Level",
        "Next Steps",
        "KPIs",
        "Metrics Driven",
        "Deliver on Expectations",
        "Shift Left",
        "Customer Journey",
        "Strategic Initiative",
        "Scalable Solution",
        "Thought Partner",
        "Core Competency",
        "Value Proposition",
        "Growth Mindset",
        "Digital Transformation",
        "Operational Excellence",
        "Agile Framework",
        "Holistic View",
        "Enterprise Ready",
        "Cross Functional",
        "Runway",
        "Buy vs Build",
        "Right Hand Left Hand",
        "Trust but Verify",
        "Swivel Chair",
        "Table Stakes",
        "Hard Stop",
        "Soft Launch",
        "Big Picture",
        "Zoom Out",
        "Quick Sync",
        "Weekly Cadence",
        "Executive Summary",
        "Stakeholder Alignment",
        "Resource Constraints",
        "Capacity Planning",
        "Change Management",
        "Continuous Improvement",
        "Customer First",
        "Solution Oriented",
        "Outcome Based",
        "Data Driven",
        "Best in Class",
        "Force Multiplier",
        "Value Stream",
        "Strategic Fit",
        "Business Case",
        "Operating Model",
        "People Process Technology",
        "Plain Vanilla",
        "Full Stack",
        "Zero Trust",
        "Single Source of Truth",
        "Feedback Loop",
        "Run the Numbers",
        "Raise the Bar",
        "Move Fast",
        "Fail Fast",
        "Lessons Learned",
        "Net New",
        "Back to Basics",
        "End to End",
        "Future Proof",
        "Right the Ship",
        "First Principles",
        "Tiger Team",
        "Skin in the Game",
        "Double Click",
        "Peel the Onion",
        "Move the Goalposts",
        "Rubber Meets the Road",
        "Drink Our Own Champagne",
        "Eating Our Own Dog Food",
        "Golden Handcuffs",
        "Ivory Tower",
        "Burning Platform",
        "Lift and Shift",
        "Rip and Replace",
        "Greenfield",
        "Brownfield",
        "Tribal Knowledge",
        "Dotted Line",
        "Solid Line",
        "Air Cover",
        "Top Down",
        "Bottom Up",
        "Land and Expand",
        "Land the Plane",
        "Cutting Edge",
        "Bleeding Edge",
        "Leading Edge",
        "Trailing Edge",
        "Front Burner",
        "Back Burner",
        "On My Radar",
        "Off My Radar",
        "Punch Above Our Weight",
        "Punch List",
        "Shopping List",
        "Wish List",
        "Must Have",
        "Nice to Have",
        "Non Starter",
        "Deal Breaker",
        "Show Stopper",
        "Smoke Test",
        "Sanity Check",
        "Gut Check",
        "Temperature Check",
        "Litmus Test",
        "Acid Test",
        "Proof of Concept",
        "Minimum Viable Product",
        "Go to Market",
        "Time to Market",
        "First Mover Advantage",
        "Fast Follower",
        "Blue Ocean",
        "Red Ocean",
        "White Space",
        "Greenspace",
        "Market Share",
        "Mind Share",
        "Wallet Share",
        "Top of Mind",
        "Top Tier",
        "Second Tier",
        "Best of Breed",
        "Jack of All Trades",
        "One Stop Shop",
        "Soup to Nuts",
        "Cradle to Grave",
        "Farm to Table",
        "Bench Strength",
        "Bench Depth",
        "Talent Pipeline",
        "War for Talent",
        "Culture Fit",
        "Culture Add",
        "Employee Experience",
        "Employee Journey",
        "Servant Leadership",
        "Command and Control",
        "Matrix Organization",
        "Flat Organization",
        "Span of Control",
        "Circle of Influence",
        "Sphere of Influence",
        "Playing Politics",
        "Managing Up",
        "Managing Across",
        "Manage Expectations",
        "Set Expectations",
        "Under Promise Over Deliver",
        "Exceed Expectations",
        "Knock It Out of the Park",
        "Hit a Home Run",
        "Slam Dunk",
        "Layup",
        "Hail Mary",
        "Fourth Quarter",
        "Two Minute Drill",
        "Full Court Press",
        "Championship Mindset",
        "Participation Trophy",
        "Raise Your Hand",
        "Roll Up Your Sleeves"
    ]
    
    root = tk.Tk()
    root.geometry("700x850")
    root.minsize(600, 750)
    app = BingoUI(root, buzzwords)
    root.mainloop()


if __name__ == "__main__":
    main()
