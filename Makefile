.PHONY: all

train-flowers17-simplified:
	python main.py --dataset 17flowers_simplified --input_height=128 --is_crop True --input_fname_pattern "*.png" --is_train --samples_rate=100 --checkpoint_rate=100 --epoch 1000

test-flowers17-simplified:
	python main.py --dataset 17flowers_simplified --input_height=128 --is_crop True --input_fname_pattern "*.png"

gif: gif-train gif-arrange

gif-train: clean-train
	@echo "Create training gif animation" && \
	if [ -n "$(shell find samples -maxdepth 1 -type f \( -name "train_*.png" \))" ]; then \
	convert -delay 10 samples/train_*.png samples/animated_training.gif; \
	fi

gif-arrange: clean-arrange
	@echo "Create arrange gif animation" && \
	if [ ! -z "$(shell find samples -maxdepth 1 -type f \( -name "test_arrange_*.png" \))" ]; then \
	convert -delay 10 samples/test_arrange_*.png samples/animated_arrange.gif; \
	fi

mp4: mp4-train mp4-arrange

mp4-train: gif-train
	@echo "Create training mp4 movie" && \
	if [ -f samples/animated_training.gif ]; then \
	ffmpeg -f gif -i samples/animated_training.gif -c:v libx264 -vf fps=30 -pix_fmt yuv420p samples/animated_training.mp4; \
	fi

mp4-arrange: gif-arrange
	@echo "Create arrange mp4 movie" && \
	if [ -f samples/animated_arrange.gif ]; then \
	ffmpeg -f gif -i samples/animated_arrange.gif -c:v libx264 -vf fps=30 -pix_fmt yuv420p samples/animated_arrange.mp4; \
	fi

clean: clean-train clean-arrange

clean-train:
	@echo "Clean training animation" && \
	rm -f samples/animated_training.*

clean-arrange:
	@echo "Clean arrange animation" && \
	rm -f animated_arrange.*

pack-models:
	@echo "Compress models" && \
	zip DCGAN-models.zip -r checkpoint

pack-samples: mp4
	@echo "Compress samples" && \
	zip DCGAN-samples.zip samples/*.gif samples/*.mp4 samples/*.png

publish: publish-models publish-samples

publish-models: pack-models
	@echo "Publish models" && \
	rm -f /home/ubuntu/DCGAN-models.zip && \
	mv DCGAN-models.zip /home/ubuntu

publish-samples: pack-samples
	@echo "Publish samples" && \
	rm -f /home/ubuntu/DCGAN-samples.zip && \
	mv DCGAN-samples.zip /home/ubuntu
