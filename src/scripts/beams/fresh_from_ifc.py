import src.scripts.beams.upload_beams as upload_beams
import src.scripts.beams.beams_to_json as beams_to_json
import src.scripts.beams.beams_to_single_ifc as beams_to_single_ifc

if __name__ == "__main__":
    # beams_to_single_ifc.main()
    beams_to_json.main()
    upload_beams.main()