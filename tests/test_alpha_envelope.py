if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compute_alpha_envelope.py <latlon.npz>")
        sys.exit(1)
    compute_alpha_envelope(sys.argv[1], alpha = 0.)
