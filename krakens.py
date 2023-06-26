import sge
import game
import objects

menu = True
retry = False

def run_game():
    if game.SCORES != 0:
        game.SCORES =0
    # Create Game object
    if (retry == False):
        game.SpaceGame()
    game.DOUBLE_SHOOT = False
    game.TRIPLE_SHOOT = False
    game.LASER_SHOT = False
    game.DOUBLE_LASER_SHOT = False
    # Load backgrounds pada aset bernama final_space.jpg
    wall_sprite = sge.gfx.Sprite(name='final_space')
    layers = [sge.gfx.BackgroundLayer(wall_sprite, 0, 0)]
    background = sge.gfx.Background(layers, sge.gfx.Color('black'))
    if menu == False :
        # Menggenerate warna objek
        # Kraken nantinya akan menghasil kan berbagai macam warna random yang sudah dibuat
        colors = [(255, 0, 0),  # Red
                (0, 0, 255),  # Blue
                (0, 255, 0),  # Green
                (255, 255, 0),  # Yellow
                (255, 165, 255),  # Pink
                (128, 0, 128)]  # Purple
        krakens = [objects.Kraken(colors=colors.pop()) for _ in range(6)]
        player = objects.Player()

        # PLayer menjadi objek yang pertama
        obj = [player] + krakens

        # Create room
        sge.game.start_room = game.GameRoom(obj, background=background)

        # Mouse dibuat invisible atau tak terliat yang berguna untuk mengatasi collision
        sge.game.mouse.visible = False
        sge.game.start_room.remove(sge.game.mouse)
    elif menu == True:
        sge.game.start_room = game.GameRoom( background=background)

    # Game telah dimulai! Yey!
    sge.game.start()

if __name__ == '__main__':
    run_game()



