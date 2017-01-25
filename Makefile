.PHONY: all

train-flowers17-simplified:
	python main.py --dataset 17flowers_simplified --input_height=128 --is_crop True --input_fname_pattern "*.png" --is_train --samples_rate=100 --checkpoint_rate=100 --epoch 2500

test-flowers17-simplified:
	python main.py --dataset 17flowers_simplified --input_height=128 --is_crop True --input_fname_pattern "*.png"

gif:
	convert -delay 10 samples/train_*.png samples/animated_training.gif

mp4:
	ffmpeg -f gif -i samples/animated_training.gif -c:v libx264 -vf fps=30 -pix_fmt yuv420p samples/animated_training.mp4

clean:
	rm -rf test_arange_*.*

publish:
	zip DCGAN-smples.zip samples/animated_training.* && \
	mv DCGAN-smples.zip /home/ubuntu
