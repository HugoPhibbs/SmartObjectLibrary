import src.scripts.objects.upload_from_json as upload_beams
import src.scripts.objects.ifc_to_json as beams_to_json
import src.scripts.objects.parse_building_ifc_to_single_ifc as beams_to_single_ifc

if __name__ == "__main__":
    # beams_to_single_ifc.main()
    beams_to_json.main()
    upload_beams.main()