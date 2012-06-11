#include <squish.h>

typedef unsigned char u8;

extern "C" {
	void CompressMasked( u8 const* rgba, int mask, void* block, int flags ) {
		squish::CompressMasked(rgba, mask, block, flags);
	}

	void Compress( u8 const* rgba, void* block, int flags ) {
		squish::Compress(rgba, block, flags);
	}

	void Decompress( u8* rgba, void const* block, int flags ) {
		squish::Decompress(rgba, block, flags);
	}

	int GetStorageRequirements( int width, int height, int flags ) {
		return squish::GetStorageRequirements(width, height, flags);
	}

	void CompressImage( u8 const* rgba, int width, int height, void* blocks, int flags ) {
		squish::CompressImage(rgba, width, height, blocks, flags);
	}

	void DecompressImage( u8* rgba, int width, int height, void const* blocks, int flags ) {
		squish::DecompressImage(rgba, width, height, blocks, flags);
	}
}
