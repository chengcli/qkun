
if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: python oci_get_latlon.py <input.nc> [output.yaml]")
        sys.exit(1)

    if len(sys.argv) == 2:
        oci_get_latlon(sys.argv[1])
    else:
        oci_get_latlon(sys.argv[1], sys.argv[2])
