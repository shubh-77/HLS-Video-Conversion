import os

import ffmpeg

renditions = [
            # {'name': '240p', 'resolution': '426x240', 'bitrate': '400k', 'audiorate': '64k'},
            # {'name': '360p', 'resolution': '640x360', 'bitrate': '700k', 'audiorate': '96k'},
            # {'name': '480p', 'resolution': '854x480', 'bitrate': '1250k', 'audiorate': '128k'},
            {'name': '720p', 'resolution': '1280x720', 'bitrate': '2500k', 'audiorate': '128k'},
            # {'name': 'HD 720p 60fps', 'resolution': '1280x720', 'bitrate': '3500k', 'audiorate': '128k'},
            {'name': '1080p', 'resolution': '1920x1080', 'bitrate': '4500k', 'audiorate': '192k'},
            # {'name': 'Full HD 1080p 60fps', 'resolution': '1920x1080', 'bitrate': '5800k', 'audiorate': '192k'},
            # {'name': '4k', 'resolution': '3840x2160', 'bitrate': '14000k', 'audiorate': '192k'},
            # {'name': '4k 60fps', 'resolution': '3840x2160', 'bitrate': '23000k', 'audiorate': '192k'}
        ]

def convert_to_hls(input_file,segment_format='%03d.ts',output_dir='cambridge-HLS'):
        
        ffmpeg_input_stream = ffmpeg.input(input_file)
        ffmpeg_output_streams = []

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for rendition in renditions:
            ffmpeg_params = {
                'vf': "scale=w={}:h={}:force_original_aspect_ratio=decrease".format(
                    rendition['resolution'].split('x')[0], rendition['resolution'].split('x')[1]),
                'c:a': 'aac',
                'ar': '48000',
                'c:v': 'h264',
                'profile:v': 'main',
                'crf': '20',
                'sc_threshold': '0',
                'g': '48',
                'keyint_min': '48',
                'hls_time': '4',
                'hls_playlist_type': 'vod',
                'b:v': f"{rendition['bitrate']}",
                'maxrate': '856k',
                'bufsize': '1200k',
                'b:a': f"{rendition['audiorate']}",
                'hls_segment_filename': f"{output_dir}/{rendition['resolution'].split('x')[1]}p_{segment_format}"
            }

            ffmpeg_output_streams.append(
                ffmpeg.output(
                    ffmpeg_input_stream,
                    f"{output_dir}/{rendition['resolution'].split('x')[1]}p.m3u8",
                    **ffmpeg_params
                )
            )

            output_streams = ffmpeg.merge_outputs(*ffmpeg_output_streams)
            ffmpeg.run(output_streams)
        generate_master_m3u8(output_dir)


def generate_master_m3u8(output_dir,filename="playlist.m3u8"):
    m3u8_content = '#EXTM3U\n#EXT-X-VERSION:3'
    for rendition in renditions:
         m3u8_content += f"\n#EXT-X-STREAM-INF:BANDWIDTH={str(rendition['bitrate']).replace('k', '000')}," \
                f"RESOLUTION={rendition['resolution']}\n"\
                    f"{rendition['name']}.m3u8"

    with open(f'{output_dir}/{filename}', "w") as file:
            file.write(m3u8_content)



convert_to_hls('cambridge.mp4')