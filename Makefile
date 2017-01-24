.PHONY: all

train-flowers17-simplified:
	python main.py --dataset 17flowers_simplified --input_height=128 --is_crop True --input_fname_pattern "*.png" --is_train --samples_rate=10 --checkpoint_rate=100 --epoch 2500

test-flowers17-simplified:
	python main.py --dataset 17flowers_simplified --input_height=128 --is_crop True --input_fname_pattern "*.png"

gif:
	convert -delay 10 train_*.png animated_training.gif

mp4:
	ffmpeg -f gif -i animated_training.gif -c:v libx264 -vf fps=30 -pix_fmt yuv420p animated_training.mp4

clean:
	rm -rf test_arange_*.*
